from __future__ import print_function
from nose.tools import eq_,with_setup
from .. import boss
import sys
import os
import shutil

from ontimer import event , utils, db
from datetime import datetime
from subprocess import Popen

sample_config='./sample-config.yaml'

def create_sample_config_server(abs_dir, config_file = sample_config):
    print('creating %s server in : %s' % (config_file,abs_dir))
    if os.path.isdir(abs_dir):
        shutil.rmtree(abs_dir)
    os.makedirs(abs_dir)
    dao=db.Dao(abs_dir)
    dao.create_db()
    dao.set_global_var('ipy_path','/Users/sergeyk/ipyhome/')
    dao.set_config(open(config_file).read())    
    config=dao.apply_config()
    gens = [event.Generator(config,gen_data) for gen_data in dao.load_active_generators()]
    dt=datetime(2015,2,2)
    dao.emit_event(gens[1].setupEvent(dt))
    return dao
    

def test_app():
    test_dir = os.path.abspath('./test-out/test_app')
    dao = create_sample_config_server(test_dir)
    Popen(['coverage', 'run', '-p','-m', 'ontimer.app', 
           '--root', test_dir,  
           '--port', '9766' , 'server']) 
    Popen(['coverage', 'run', '-p','-m', 'ontimer.app', 
           '--root', test_dir, '--quiet', 'get_conf']) 
    Popen(['coverage', 'run', '-p','-m', 'ontimer.app', 
           '--root', test_dir, '--quiet', '--config',sample_config, 'set_conf', ]) 

    import time
    time.sleep(50) 
    Popen(['coverage', 'run',  '-p','-m', 'ontimer.app', '--root', test_dir, 'shutdown'])
    time.sleep(2) 


if __name__ == '__main__':
    create_sample_config_server(os.path.abspath(sys.argv[1])) 

