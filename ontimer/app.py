from __future__ import print_function

from . import OnExp

import datetime
from tornado import websocket, web, ioloop
import json
import yaml
import argparse
import sys
import os
from .db import db_exists, connect_db, Dao

cl = []

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

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    #(r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
])

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def main():
    root = None
    def check_root(args):
        print( 'root' ) 
        return db_exists(root)
    
    def set_conf(args):
        print ( 'set_conf', args)
    
    def server(args):
        if not(db_exists(root)) or args.config :
            set_conf(args)
        print ('server', args)

    def get_conf(args):
        if args.config:
            raise ValueError('--config not supposed to be defined')
        
    parser = argparse.ArgumentParser(description='OnTimer - runs stuff on time')
    subparsers = parser.add_subparsers()
    subparsers.add_parser('server',help='starts ontimer server, if --config is defined load new config before start').set_defaults(func=server)
    subparsers.add_parser('get_conf',help='retrive most recent CONFIG out of ontimer db and stdout it').set_defaults(func=get_conf)
    subparsers.add_parser('set_conf',help='apply CONFIG to ontimer db').set_defaults(func=set_conf)
    parser.add_argument("--root", type=str, default='.', help='ontimer root dir to store db and artifacts. if not provided current directory will be used as default.')
    parser.add_argument("--config", type=str, help='config file to use. if not provided stdin/out will be used.')
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    try:
        args.func(args)
    except ValueError, e:
        warning(e)
        parser.print_help()

if __name__ == '__main__':
    main()    
#     app.listen(8899)
#     def callback():
#       print "dt=%s" %( datetime.datetime.now() )
#  
#     #milliseconds
#     interval_ms = 5 * 1000
#     main_loop = ioloop.IOLoop.instance()
#     scheduler = ioloop.PeriodicCallback(callback,interval_ms, io_loop = main_loop)
#     #start your period timer
#     scheduler.start()
#     main_loop.start()
