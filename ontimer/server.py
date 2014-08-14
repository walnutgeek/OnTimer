'''
Server module
running on websocket and static file web interface on tornado. 
Same tornado ioloop managing concurrent jobs and recording 
out/err streams in files.
'''
from tornado import websocket, web, ioloop, iostream
import socket
import datetime
import json
import yaml
import functools
import os
import fcntl
import sys

from . import event
from .db import Dao
from .utils import quict
import shlex, subprocess

_IN_STREAM = 0
_OUT_FILE = 1
_COUNTER = 2
_NAME = 3

def set_non_blocking(f): 
    fd = f.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    return f

def read_stream(run, idx, fd, events):
    buf = fd.read()
    if len(buf):
        run.streams[idx][_OUT_FILE].write(buf)
        p = run.streams[idx][_COUNTER] + len(buf)
        run.state.dao.add_artifact_score(quict(event_task_id=run.task['event_task_id'], run=run.task['run_count'], name=run.streams[idx][3], score=p))
        run.streams[idx][_COUNTER] = p 

class Run:
    def __init__(self,state, task):
        self.state = state
        self.task = task
        self.update_task( _run_count = task['run_count'] + 1 , _task_status = event.TaskStatus.running )
        self.task_state = json.loads(self.task['task_state'])
        self.args = shlex.split(self.task_state['cmd'])
        self.task_vars = event.task_vars(self.task)
        self.rundir = self.state.config.globals['logs_dir'].format(**self.task_vars)
        os.makedirs(self.rundir)
        self.process = subprocess.Popen(self.args, cwd=self.rundir, stderr=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
        print 'started task_id=%d cmd=%s' % ( self.task['event_task_id'], self.task_state['cmd'])
        
        self.streams = ( 
             [ set_non_blocking(self.process.stdout), None, 0, 'out'],
             [ set_non_blocking(self.process.stderr), None, 0, 'err'],
        )
        for stream in self.streams:
            stream[_OUT_FILE] = open(os.path.join(self.rundir,'%s_stream' % stream[_NAME] ),'w')
        io_loop = ioloop.IOLoop.instance()
        for idx in range(2):
            io_loop.add_handler(self.streams[idx][_IN_STREAM], functools.partial(read_stream, self, idx), io_loop.READ)

    def update_task(self, **kwargs):
        self.task.update(**kwargs)
        if self.state.dao.update_task(self.task):
            self.task = state.dao.load_task(self.task)
        else:
            raise ValueError('task already processed by somewhere else %r' % self.task)
            
    def stillRunning(self):
        if self.process.poll() or self.process.returncode is not None :
            # clean up
            rc = self.process.returncode
            print 'finished rc=%d task_id=%d' % (rc , self.task['event_task_id'])
            self.state.dao.store_artifact(quict(event_task_id=self.task['event_task_id'], run=self.task['run_count'], name='return_code', value=rc))
            if rc == 0:
                self.update_task(_task_status = event.TaskStatus.success,_last_run_outcome = event.RunOutcome.success )
            else:
                self.update_task(_task_status = event.TaskStatus.fail,_last_run_outcome = event.RunOutcome.fail )
            io_loop = ioloop.IOLoop.instance()
            for idx in range(2):
                io_loop.remove_handler(self.streams[idx][_IN_STREAM])
                for f in self.streams[idx][_IN_STREAM:_OUT_FILE]:
                    f.close()
            return False
        return True
                
        
class State:
    def __init__(self, dao):
        self.dao = dao
        self.clients = []
        self.config = self.dao.apply_config()
        self.tasks = None
        self.events = None
        self.json = None
        self.runs = []
        event.global_config.update(self.dao.get_global_vars())
    
    def check(self):
        for task in self.dao.get_tasks_to_run():
            self.runs.append(Run(self,task))
        self.runs = [run for run in self.runs if run.stillRunning()]
        #retry failed tasks
        for task in self.dao.get_tasks_of_status(event.TaskStatus.fail):
            next_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=5 * task['run_count'])
            task.update( _task_status = event.TaskStatus.retry, _run_at_dt = next_time )
            self.dao.update_task(task)
        #finish events
        for ev in self.dao.get_events_to_be_completed():
            ev.update( _event_status = event.EventStatus.success, _finished_dt = datetime.datetime.utcnow() )
            self.dao.update_event(ev)
            
        tasks,taskdict = self.dao.get_active_events()
        json_data = json.dumps(tasks)
        if json_data != self.json:
            self.taskdict = taskdict
            self.tasks = tasks
            self.json = json_data
            self.pushAll()
    
    def pushAll(self):
        for client in self.clients:
            self.pushToOne(client)
            
    def pushToOne(self,client):
            if self.json:
                #print "dt=%s sending=%s" % ( datetime.datetime.now() , self.json )
                client.write_message(self.json)        

    def addClient(self,client):
        if client not in self.clients:
            self.clients.append(client)
            self.pushToOne(client)

    def removeClient(self,client):
        if client in self.clients:
            self.clients.remove(client)
            
    def emit_event(self,event_string):
        self.dao.emit_event( event.Event.fromstring(self.config,event_string) )


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("web/index.html")

class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        state.addClient(self)

    def on_close(self):
        state.removeClient(self)


class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        event_str = self.get_argument("event")
        state.emit_event(event_str)
        state.check()
        
    @web.asynchronous
    def post(self):
        pass



class FileHandler(web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

def run_server(_dao):
    global state
    state = State(_dao)
    state.check()
    webpath = os.path.join(os.path.dirname(__file__),'web')
    print 'webpath=%s' % webpath
    app = web.Application([
        (r'/', IndexHandler),
        (r'/ws', SocketHandler),
        (r'/api', ApiHandler),
        (r"/(.*)", FileHandler,  {"path": webpath})
    ])
    try:
        app.listen(9753)
    except socket.error, e:
        print e
        raise SystemExit(-1)
    #milliseconds
    interval_ms = 5 * 1000
    main_loop = ioloop.IOLoop.instance()
    scheduler = ioloop.PeriodicCallback(lambda: state.check() , interval_ms, io_loop = main_loop)
    #start your period timer
    scheduler.start()
    main_loop.start()
