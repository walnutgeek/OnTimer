import os
import shutil
import unittest
import time


from nose.tools import eq_,with_setup
from .. import OnExp, OnState, event
from collections import defaultdict


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()

test_dir = os.path.abspath("test-out")
if os.path.isdir(test_dir):
    shutil.rmtree(test_dir)
os.mkdir(test_dir)

from ontimer.db import Dao
dao = Dao(test_dir,filename="test.db")
eq_(1, dao.query('pragma foreign_keys')[0][0])
dao.create_db()

def test_dbcreation():
    c1_text = open("ontimer/tests/test-config.yaml","r").read()
    c2_text = open("ontimer/tests/test-config-v2.yaml","r").read()
    eq_(1, len(dao.query('select * from settings')))
    eq_(None,dao.get_config())
    dao.set_config(c1_text)
    eq_(1,dao.get_config()[0])
    eq_(c1_text,dao.get_config()[2])
    dao.set_config(c1_text)
    eq_(1,dao.get_config()[0])
    eq_(c1_text,dao.get_config()[2])
    dao.apply_config()
    dao.set_config(c2_text)
    eq_(2,dao.get_config()[0])
    eq_(c2_text,dao.get_config()[2])
    dao.apply_config()
    c2_text = open("sample-config.yaml","r").read()
    dao.set_config(c2_text)
    eq_(3,dao.get_config()[0])
    eq_(c2_text,dao.get_config()[2])
    dao.apply_config()

def test_set_global_var():
    dao.set_global_var('ipy_path', '/Users/sergeyk/ipyhome1')
    eq_("{u'ipy_path': u'/Users/sergeyk/ipyhome1'}", repr(dao.get_global_vars()) )
    dao.set_global_var('ipy_path', '/Users/sergeyk/ipyhome')
    eq_("{u'ipy_path': u'/Users/sergeyk/ipyhome'}", repr(dao.get_global_vars()) )
    event.global_config.update(dao.get_global_vars())
        
    
def test_emit():
    conf = dao.apply_config()
    ev = event.Event.fromstring(conf,"price,us,20140713")
    dao.emit_event(ev)
    
def test_active_events():
    dao.get_active_events()
    
def test_get_tasks_to_run():
    r=dao.get_tasks_to_run()
    eq_(1,len(r))
    t1 = r[0]
    et_id = t1['event_task_id']
    eq_(1,et_id)
    artifact = { 'event_task_id' : et_id, 
                 'run' : 1,
                'name' : 'key',
                'value' : 'value'
            }
    dao.store_artifact(artifact)
    score = { 'event_task_id' : et_id,
               'run' : 1,
               'name' : 'score',
               'score' : 17 }
    dao.add_artifact_score(score)
    score['score'] = 21
    dao.add_artifact_score(score)
    artifact['value'] = 'vv'
    dao.store_artifact(artifact)
    t1['_task_status'] = event.TaskStatus.running
    eq_(True,dao.update_task(t1))
    r=dao.get_tasks_to_run()
    eq_(0,len(r))
    t1['_task_status'] = event.TaskStatus.success
    eq_(False,dao.update_task(t1))
    t1 = dao.load_task(t1)
    t1['_task_status'] = event.TaskStatus.success
    eq_(True,dao.update_task(t1))
    r=dao.get_tasks_to_run()
    eq_(1,len(r))
    t2 = r[0]
    et_id2 = t2['event_task_id']
    eq_(2,et_id2)
    tasks,tasksdict=dao.get_active_events()
    ev = tasks[1]
#     ev=events[1]
    ev['_event_status']=event.EventStatus.fail
    eq_(True,dao.update_event(ev))
    dao.load_task({'event_task_id':et_id2})
    
 
        

