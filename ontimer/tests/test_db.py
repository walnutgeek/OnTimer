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

from .. import db
from ..db import Dao
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
    dao.get_event_tasks()
    
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
    events,tasksdict=dao.get_event_tasks()
    eq_(1,len(events))
    ev = events[0]
#     ev=events[1]
    ev['_event_status']=event.EventStatus.fail
    eq_(True,dao.update_event(ev))
    dao.load_task({'event_task_id':et_id2})
    
 
def test__fetch_tree():
    query_result = [[1,1,1],[1,2,1],[1,2,2],[1,2,1],[2,1,1],[3,1,2]]
    query_columns = ['a','b','c']
    eq_("[{'a': 1, 'bees': [{'b': 1, 'sees': [{'c': 1}]}, {'b': 2, 'sees': [{'c': 1}, {'c': 2}, {'c': 1}]}]}, "+
         "{'a': 2, 'bees': [{'b': 1, 'sees': [{'c': 1}]}]}, " +
         "{'a': 3, 'bees': [{'b': 1, 'sees': [{'c': 2}]}]}]",
         '%r' % db._fetch_tree(None, ( ('b','bees'),('c','sees') ), 
                                  query_columns =query_columns,
                                  query_result = query_result ) )

def test_generators():
    gs = dao.load_active_generators()
    eq_("[{'prev_event_id': None, 'current_event_id': None, 'ontime_state': None, 'event_name': u'price', 'generator_name': u'us', 'current_event': None, 'event_type_id': 1, 'generator_id': 1, 'last_seen_in_config_id': 3}, " +
         "{'prev_event_id': None, 'current_event_id': None, 'ontime_state': None, 'event_name': u'tree', 'generator_name': u'10am', 'current_event': None, 'event_type_id': 2, 'generator_id': 3, 'last_seen_in_config_id': 3}]", repr(gs))
    conf = dao.apply_config()
    ev = event.Event.fromstring(conf,"tree,20140713")
    ev.generator = gs[1]
    dao.emit_event(ev)
    gs = dao.load_active_generators()
    eq_(True, gs[1]['current_event'] is not None)
    cur_ev = gs[1]['current_event']
    del gs[1]['current_event']
    cur_ev['started_dt'] = None
    eq_("{'updated_dt': None, 'event_string': u'tree,2014-07-13 00:00:00', 'event_id': 2, 'eta_dt': None, 'started_dt': None, 'event_type_id': 2, 'generator_id': 3, 'event_status': 1, 'finished_dt': None}", repr(cur_ev))

    eq_("[{'prev_event_id': None, 'current_event_id': None, 'ontime_state': None, 'event_name': u'price', 'generator_name': u'us', 'current_event': None, 'event_type_id': 1, 'generator_id': 1, 'last_seen_in_config_id': 3}, " +
         "{'prev_event_id': None, 'current_event_id': %d, 'ontime_state': None, 'event_name': u'tree', 'generator_name': u'10am', 'event_type_id': 2, 'generator_id': 3, 'last_seen_in_config_id': 3}]"
         %(cur_ev['event_id'])
         , repr(gs))
       

