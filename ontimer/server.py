'''
Created on Jul 21, 2014

@author: sergeyk
'''
from tornado import websocket, web, ioloop
import socket
import datetime
import json
import yaml
from . import event
from .db import Dao



cl = []
dao = None
config = None
active_events = None

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("web/index.html")

class SocketHandler(websocket.WebSocketHandler):

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

def push_status():
    data = dao.get_status()
    data = json.dumps(data)
    for c in cl:
        c.write_message(data)

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        event_str = self.get_argument("event")
        dao.emit_event(event.Event.fromstring(config,event_str))
        push_status()
    @web.asynchronous
    def post(self):
        pass
    
def callback(): print "interval callback dt=%s" % (datetime.datetime.now() )

def run_server(_dao):
    dao = _dao
    config = dao.apply_config()
    active_events = dao.get_active_events()
    
    app = web.Application([
        (r'/', IndexHandler),
        (r'/ws', SocketHandler),
        (r'/api', ApiHandler),
        (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
        #(r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
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
