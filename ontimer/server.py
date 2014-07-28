'''
Created on Jul 21, 2014

@author: sergeyk
'''
from tornado import websocket, web, ioloop
import socket
import datetime
import json
import yaml
import os
from . import event
from .db import Dao



class State:
    def __init__(self, dao):
        self.dao = dao
        self.clients = []
        self.config = self.dao.apply_config()
        self.types = None
        self.events = None
        self.types = None
        self.json = None
        event.global_config.update(self.dao.get_global_vars())
    
    def check(self):
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
                print "dt=%s sending=%s" % ( datetime.datetime.now() , self.json )
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

def callback(): 
    state.check()


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
    scheduler = ioloop.PeriodicCallback(callback, interval_ms, io_loop = main_loop)
    #start your period timer
    scheduler.start()
    main_loop.start()
