
from nose.tools import eq_
from .. import event
from .. import utils
import datetime
import json
from collections import defaultdict

def test_yaml():
    s = open("ontimer/tests/test-config.yaml","r").read()
    conf = event.Config(s)
    eq_('price',conf.events[0].name)

split_join_cases = [
                    ('',['']),
                    ('a',['a']),
                    ('a,b',['a','b']),
                    ('a\\,b',['a,b']),
                    ('a\\\\b',['a\\b']),
                    ('a\\\\b,c',['a\\b','c']),
                    ]

def test_split_join():
    for case in split_join_cases:
        eq_(case[1],event.splitEventString(case[0]))
        eq_(case[0],event.joinEventString(case[1]))
        
def test_Event_obj():
    conf = event.Config(open("ontimer/tests/test-config.yaml","r").read())
    e=event.Event.fromstring(conf,"price,us,20140713")
    eq_("price,us,2014-07-13 00:00:00",str(e))
    tasks = e.tasks()
    eq_(2,len(tasks))

def test_joinEnumsIndices():
    eq_("1,3",event.joinEnumsIndices(event.EventStatus,event.MetaStates.active))
    eq_("1,2,3,4",event.joinEnumsIndices(event.TaskStatus,event.MetaStates.active))
    eq_("1,2,3,4,11,101,102",event.joinEnumsIndices(event.TaskStatus,event.MetaStates.all))
    eq_("3,101,102",event.joinEnumsIndices(event.RunOutcome,event.MetaStates.all))
    eq_(event.TaskStatus.success,event.RunOutcome.success)

def test_get_meta():
    eq_('{"TaskStatus": {"scheduled": 1, "retry": 4, "success": 101, "skip": 102, "paused": 11, "running": 2, "fail": 3}, "EventStatus": {"active": 1, "fail": 3, "paused": 11, "success": 101, "skip": 102}, "MetaStates": {"active": 2, "ready": 3, "all": 0, "final": 1}}', json.dumps(event.get_meta()))

def test_enums():
    eq_(event.TaskStatus.success,utils.find_enum(event.TaskStatus, 'success'))
    eq_(event.TaskStatus.success,utils.find_enum(event.TaskStatus, 101))
