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
from . import event
from .db import Dao
from .utils import quict
import shlex, subprocess

def read_stream(run, idx, fd, events):
    buf = fd.read()
    run.streams[idx][1].write(buf)
    p = run.streams[idx][2] + len(buf)
    run.state.dao.add_artifact_score(quict(event_task_id=run.task['event_task_id'], run=run.task['run_count'], name=run.streams[idx][3], score=p))
    run.streams[idx][2] = p 

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
        self.process = subprocess.Popen(self.args, cwd=self.rundir, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.streams = ( [self.process.stdout,open(os.path.join(self.rundir,'out_stream'),'w'),0 ,'out'],
                         [self.process.stderr,open(os.path.join(self.rundir,'err_stream'),'w'),0 ,'err'],
                         )
        io_loop = ioloop.IOLoop.instance()
        for idx in range(2):
            io_loop.add_handler(self.streams[idx][0], functools.partial(read_stream, self, idx), io_loop.READ)

    def update_task(self, **kwargs):
        self.task.update(**kwargs)
        if self.state.dao.update_task(self.task):
            self.task = state.dao.load_task(self.task)
        else:
            raise ValueError('task already processed by somewhere else %r' % self.task)
            
    def stillRunning(self):
        if self.process.poll():
            # clean up
            rc = self.process.returncode
            self.state.dao.add_artifact_score(quict(event_task_id=self.task['event_task_id'], run=self.task['run_count'], name='return_code', score=rc))
            if rc == 0:
                self.update_task(_task_status = event.TaskStatus.success,_last_run_outcome = event.RunOutcome.success )
            else:
                self.update_task(_task_status = event.TaskStatus.fail,_last_run_outcome = event.RunOutcome.fail )
            io_loop = ioloop.IOLoop.instance()
            for idx in range(2):
                io_loop.remove_handler(self.streams[idx][0])
                for f in self.streams[idx][0:1]:
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
        self.types = None
        self.json = None
        self.runs = []
        event.global_config.update(self.dao.get_global_vars())
    
    def check(self):
        for task in self.dao.get_tasks_to_run():
            self.runs.append(Run(self,task))
        self.runs = [run for run in self.runs if run.stillRunning()]
        types,events,tasks = self.dao.get_active_events()
        json_data = json.dumps(types)
        if json_data != self.json:
            self.types = types
            self.events = events
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
