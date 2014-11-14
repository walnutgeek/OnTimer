from nose.tools import eq_,with_setup
from .. import boss
import sys
import os
import shutil

from ontimer import event , utils, db
from datetime import datetime
from subprocess import Popen
def test_app():
    test_dir = os.path.abspath('./test-out/test_app')
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    dao=db.Dao(test_dir)
    dao.create_db()
    dao.set_global_var('ipy_path','/Users/sergeyk/ipyhome/')
    dao.set_config(open('./sample-config.yaml').read())    
    config=dao.apply_config()
    gens = [event.Generator(config,gen_data) for gen_data in dao.load_active_generators()]
    import datetime
    dt=datetime.datetime(2014,9,15)
    dao.emit_event(gens[1].setupEvent(dt))
    Popen(['coverage', 'run', '-p','-m', 'ontimer.app', 
           '--root', test_dir, 
           '--port', '9766' ,'--quiet', 'server'])
    import time
    time.sleep(10) 
    Popen(['coverage', 'run',  '-p','-m', 'ontimer.app', '--root', test_dir, '--quiet', 'shutdown'])
    time.sleep(2) 


