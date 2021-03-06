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
from sets import Set
import sys

from . import dpt
from . import event
from .db import Dao, ServerStatus
from . import utils
import shlex, subprocess

import logging
log = logging.getLogger(__name__)


_IN_STREAM = 0
_OUT_FILE = 1
_COUNTER = 2
_NAME = 3

def set_non_blocking(f): 
    fd = f.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK | os.O_SYNC )
    return f

def read_stream(run, idx, fd, events):
    buf = fd.read()
    if len(buf):
        os.write(run.streams[idx][_OUT_FILE],buf)
        p = run.streams[idx][_COUNTER] + len(buf)
        run.addArtifactScore(run.streams[idx][3],p)
        run.streams[idx][_COUNTER] = p 
    else:
        run.isRunning()

class Run:
    def __init__(self,state, task):
        self.state = state
        self.task = task
        self.update_task( _run_count = task['run_count'] + 1 , _task_status = event.TaskStatus.running )
        self.task_state = json.loads(self.task['task_state'])
        self.args = shlex.split(self.task_state['cmd'].strip())
        self.task_vars = event.task_vars(self.task)
        self.rundir = self.state.config.globals['logs_dir'].format(**self.task_vars)
        self.finished = False
        os.makedirs(self.rundir)
        task_env=os.environ.copy()
        task_env['PYTHONUNBUFFERED']='1'
        self.process = subprocess.Popen(self.args, cwd=self.rundir, env=task_env, stderr=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
        log.info( 'started task_id=%d cmd=%s' % ( self.task['task_id'], self.task_state['cmd']))
        self.streams = ( 
             [ set_non_blocking(self.process.stdout), None, 0, 'out'],
             [ set_non_blocking(self.process.stderr), None, 0, 'err'],
        )
        io_loop = ioloop.IOLoop.instance()
        for idx, stream in enumerate(self.streams):
            stream[_OUT_FILE] = os.open(os.path.join(self.rundir,'%s_stream' % stream[_NAME] ), os.O_WRONLY | os.O_SYNC | os.O_CREAT)
            io_loop.add_handler(stream[_IN_STREAM], functools.partial(read_stream, self, idx), io_loop.READ)
        self.storeArtifacts(workdir=self.rundir,started='status')

    def update_task(self, **kwargs):
        self.task.update(**kwargs)
        if self.state.dao.update_task(self.task):
            self.task = state.dao.load_task(self.task)
        else:
            raise ValueError('task already processed somewhere else %r' % self.task)

    def storeArtifacts(self, **kwargs):
        for k in kwargs:
            self.state.dao.store_artifact(
                      utils.quict(task_id=self.task['task_id'], 
                            run=self.task['run_count'], 
                            name=k, value=kwargs[k]))

    def addArtifactScore(self, *args, **kwargs):
        for i in range(0,len(args),2):
            self.state.dao.add_artifact_score(
                      utils.quict(task_id=self.task['task_id'], 
                            run=self.task['run_count'], 
                            name=args[i], score=args[i+1]))
        for k in kwargs:
            self.state.dao.add_artifact_score(
                      utils.quict(task_id=self.task['task_id'], 
                            run=self.task['run_count'], 
                            name=k, score=kwargs[k]))
            
    def isRunning(self):
        if self.finished:
            return False
        if self.process.poll() or self.process.returncode is not None :
            self.finished = True
            # clean up
            rc = self.process.returncode
            log.info( 'finished rc=%d task_id=%d' % (rc , self.task['task_id']))
            self.storeArtifacts(finished='status',return_code = rc)
            if rc == 0:
                self.update_task(_task_status = event.TaskStatus.success,_last_run_outcome = event.RunOutcome.success )
            else:
                self.update_task(_task_status = event.TaskStatus.fail,_last_run_outcome = event.RunOutcome.fail )
            io_loop = ioloop.IOLoop.instance()
            for stream in self.streams:
                io_loop.remove_handler(stream[_IN_STREAM])
                stream[_IN_STREAM].close()
                os.close(stream[_OUT_FILE])
            return False
        return True
        
ACTION_STATUS_MAP =  {'RETRY_TREE':event.TaskStatus.retry, 'RETRY':event.TaskStatus.retry, 
                      'SKIP':event.TaskStatus.skip, 'PAUSE': event.TaskStatus.paused, 
                      'UNPAUSE':event.TaskStatus.retry, 'RUN_NOW':event.TaskStatus.retry,}

class State:
    def __init__(self, dao):
        self.dao = dao
        self.clients = []
        self.config = self.dao.apply_config()
        self.tasks = None
        self.taskdict = None
        meta = event.get_meta()
        time_letty_map = dpt.Letty.time.value['vars']
        meta['EventTypes'] = { et.event_type_id : et.name for et in self.config.events } 
        meta['EventTypes']['*']= '- All -';
        meta['TimeVars'] = { letter : time_letty_map[letter]['name'] for letter in time_letty_map} 
        self.meta_json = json.dumps({ 'meta' : meta} )
        self.json = {}
        self.runs = []
        event.global_config.update(self.dao.get_global_vars())
    
    def check(self):
        server_props = self.dao.get_server_properties()
        status = utils.find_enum(ServerStatus, server_props['server_status'])
        prepare_to_stop = status == ServerStatus.prepare_to_stop

        if not(prepare_to_stop):
            if status != ServerStatus.running:
                server_props.update(_server_status = ServerStatus.running)
                self.dao.set_server_properties(server_props)
            for task in self.dao.get_tasks_to_run():
                self.runs.append(Run(self,task))
        self.runs = [run for run in self.runs if run.isRunning()]
        if prepare_to_stop and len(self.runs)==0:
            self.main_loop.stop()
            self.scheduler.stop()
            server_props.update(_server_status = ServerStatus.shutdown )
            self.dao.set_server_properties(server_props)
            return
            
        #retry failed tasks
        for task in self.dao.get_tasks_of_status(event.TaskStatus.fail):
            next_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=5 * task['run_count'])
            task.update( _task_status = event.TaskStatus.retry, _run_at_dt = next_time )
            self.dao.update_task(task)
        #finish events
        for ev in self.dao.get_events_to_be_completed():
            ev.update( _event_status = event.EventStatus.success, _finished_dt = datetime.datetime.utcnow() )
            self.dao.update_event(ev)
        for gen_data in self.dao.load_active_generators():
            gen = event.Generator(self.config,gen_data)
            if event.GeneratorStatus.ontime == gen.status :
                ne=gen.nextEvent()
                if ne and ne.scheduled_dt < utils.utc_adjusted(hours=+12):
                    self.dao.emit_event(ne) 
        events,taskdict = self.dao.get_event_tasks()
        json_data = json.dumps({ 'get_event_tasks' : events })
        if json_data != self.json:
            self.taskdict = taskdict
            self.events = events
            self.json = json_data
            #log.debug( "sending:%s" %  self.json ) 
            self.pushAll()
    

    def change_tasks(self, apply_action, task_ids):
        if apply_action not in ACTION_STATUS_MAP:
            raise ValueError("apply_action:%r is not one of:%r" % (apply_action, ACTION_STATUS_MAP))
        _, tasks = self.dao.get_event_tasks_by_taskid(task_ids)
        selected_tasks = Set()
        for task_id in task_ids:
            selected_tasks.add(task_id)
            if apply_action == 'RETRY_TREE':
                for dependent_id in utils.flatten_links(tasks, task_id, 'dependents'):
                    selected_tasks.add(dependent_id)
        updated_tasks = {}
        for task_id in selected_tasks:
            task = tasks[task_id]
            if apply_action in ['RETRY_TREE', 'RETRY', 'RUN_NOW']:
                task.update(_run_at_dt=datetime.datetime.utcnow() + datetime.timedelta(seconds=5))
            new_status = ACTION_STATUS_MAP[apply_action]
            task.update(_task_status=new_status)
            self.dao.update_task(task)
            updated_tasks[task_id] = new_status.value
        return updated_tasks
    
    def get_file_fragment(self, fn, start=0,end=-1 ):
        if not(os.path.abspath(fn).startswith(self.dao.root)):
            raise ValueError('path:%s is outside of root:%s' % (fn,self.dao.root))
        fp=open(fn)
        count=end
        if start > 0:
            fp.seek(start,0)
            if count > 0:
                count -= start
        if count > 0:
            return fp.read(count)
        else:
            return fp.read()
    
    def pushAll(self):
        for client in self.clients:
            self.pushToOne(client,self.json)
            
    def pushToOne(self,client,content):
            if content:
                client.write_message(content)        

    def addClient(self,client):
        if client not in self.clients:
            self.clients.append(client)
            self.pushToOne(client, self.meta_json)
            self.pushToOne(client, self.json)

    def removeClient(self,client):
        if client in self.clients:
            self.clients.remove(client)
            
    def emit_event(self,event_string):
        self.dao.emit_event( event.Event.fromstring(self.config,event_string) )


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("web/app.html")

class SocketHandler(websocket.WebSocketHandler):
    
    def __init__(self,*args,**kwargs):
        self.user = None
        websocket.WebSocketHandler.__init__(self,*args,**kwargs)
        
    def open(self):
        state.addClient(self)
    
    def on_message(self,msg):
        log.debug( 'on message: %r' % msg)
        msg_dict = json.loads(msg)
        action = msg_dict['action']
        source = msg_dict['source']
        args=msg_dict['args']
        res = self.dispatch(action,source,args)
        self.write_message(json.dumps({
               'action': action,
               'source': source,                        
               'response': res }))
    
    def dispatch(self, action,source,args):
        if action == 'change' :
            if source == 'tasks' :
                return state.change_tasks(args['apply'], [ int(i) for i in args['task_id']] )
        elif action == 'get' :
            if source == 'event' :
                if 'task_id' in args:
                    return state.dao.get_event_tasks_by_taskid(args['task_id'])
                elif 'event_id' in args:
                    return state.dao.get_event_tasks_by_eventid(args['event_id'])
            elif source == 'run' :
                return state.dao.get_artifacts_for_run(int(args['task_id']),int(args['run']))
            elif source == 'file' :
                buf = state.get_file_fragment( args['file'],int(args['start']),int(args['end']))
                return { 'buf': buf, 'length' : len(buf), 'args': args  }
        elif action == 'unsubscribe' :
            if source == 'run' :
                pass
        elif action == 'subscribe' :
            if source == 'events' :
                pass
            elif source == 'run' :
                pass
        raise AssertionError('Unrecognized request: {action:%r,source:%r,args:%r}' % (action,source,args))
            
    

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

def run_server(_dao,address="",port=9753):
    global state
    state = State(_dao)
    webpath = os.path.join(os.path.dirname(__file__),'web')
    log.info( 'platform_info=%r' % (utils.platform_info()) )
    log.info( 'webpath=%s' % webpath)
    app = web.Application([
        (r'/', IndexHandler),
        (r'/event.*', IndexHandler),
        (r'/task/.*', IndexHandler),
        (r'/run/.*', IndexHandler),
        (r'/ws', SocketHandler),
        (r'/api', ApiHandler),
        (r"/(.*)", FileHandler,  {"path": webpath})
    ])
    try:
        log.info( 'port=%r, address=%r' % (port,address) )
        app.listen(port,address=address)
    except socket.error, e:
        log.exception(e) 
        raise SystemExit(-1)
    #milliseconds
    interval_ms = 5 * 1000
    server_props = _dao.get_server_properties()
    if ServerStatus.running == server_props['server_status'] :
        raise ValueError('server already running: %r' % server_props)
    log.info('reseting %d tasks' % _dao.reset_running_tasks() )
    
    server_props.update( _server_status = ServerStatus.running, 
                         _server_host = address, _server_port = port )
    _dao.set_server_properties(server_props)
    state.main_loop = ioloop.IOLoop.instance()
    state.scheduler = ioloop.PeriodicCallback(state.check , interval_ms, io_loop = state.main_loop)
    state.check()
    state.scheduler.start()
    state.main_loop.start()
