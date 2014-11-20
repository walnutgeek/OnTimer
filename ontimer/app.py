'''
OnTimer app 
+++++++++++

run scheduler daemon and web interface

to run::

  python -m ontimer.app --root root/ --config sample-config.yaml server
  

'''
from __future__ import print_function

import argparse
import sys
import os
from .db import Dao,ServerStatus
from . import server
from . import event
from . import utils
import logging

log = logging.getLogger(__name__)

def set_logging(rootdir, quiet):
    error_handler = logging.FileHandler( os.path.join(rootdir, "debug.log"), "a" )
    error_handler.setLevel(logging.DEBUG)
    error_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
    root = logging.getLogger()
    if not(quiet):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        root.addHandler(console_handler)
    root.addHandler(error_handler)
    root.setLevel(logging.DEBUG)

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)
    
def main():
    dao = None
    def shutdown(args):
        if not(dao.exists()):
            raise ValueError('cannot shutdown not running OnTimer')
        server_props = dao.get_server_properties()
        if utils.find_enum(ServerStatus, server_props['server_status'] ) != ServerStatus.running:
            raise ValueError('cannot shutdown not running OnTimer')
        server_props.update( _server_status = ServerStatus.prepare_to_stop )
        if dao.set_server_properties(server_props):
            log.info ("Shutdown initiated")
    def set_conf(args):
        if not(args.config):
            raise ValueError("config has to be defined")
        config_text=open(args.config,"r").read()
        dao.ensure_db()
        if dao.set_config(config_text) :
            log.info('new config loaded:%s' % args.config)
        
    def run_server(args):
        if not(dao.exists()) or args.config :
            set_conf(args)
        log.debug('%r %r' % ('server', args) )
        server.run_server(dao,address=args.address,port=args.port)

    def get_conf(args):
        if args.config:
            raise ValueError('--config not supposed to be defined')
        if not(dao.exists()):
            raise ValueError('db does not exists at --root location')
        print(dao.get_config()[2])
        
    parser = argparse.ArgumentParser(description='OnTimer - runs stuff on time')
    subparsers = parser.add_subparsers()
    
    subparsers.add_parser('shutdown', help='notify ontimer server to shutdown').set_defaults(func=shutdown)
    subparsers.add_parser('server',   help='starts ontimer server, if --config is defined load new config before start').set_defaults(func=run_server)
    subparsers.add_parser('get_conf', help='retrive most recent CONFIG out of ontimer db and stdout it').set_defaults(func=get_conf)
    subparsers.add_parser('set_conf', help='apply CONFIG to ontimer db').set_defaults(func=set_conf)
    parser.set_defaults(quiet=False)
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='quiet mode')
    parser.add_argument("--port", type=int, default=9753, help='ontimer will listen on that port.')
    parser.add_argument("--address", type=str, default='', help='ontimer will listen on that ip address.')
    parser.add_argument("--root", type=str, default='.', help='ontimer root dir to store db and artifacts. if not provided current directory will be used as default.')
    parser.add_argument("--config", type=str, help='config file to use.')
    args = parser.parse_args()
    abs_root = os.path.abspath(args.root)
    event.global_config.update(ontimer_root =abs_root)
    set_logging(abs_root,args.quiet)
    log.info("abs_root= %r" % abs_root)
    dao=Dao(abs_root)
    try:
        args.func(args)
    except ValueError, e:
        warning(e)
        #parser.print_help()
        raise SystemExit(-1)

if __name__ == '__main__':
    main()    
