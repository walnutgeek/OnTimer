
from nose.tools import eq_
from .. import event
import datetime
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

