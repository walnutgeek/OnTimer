
from nose.tools import eq_
from .. import event
import datetime
from collections import defaultdict

def test_yaml():
    s = open("ontimer/tests/test-config.yaml","r").read()
    conf = event.Config(s)
    eq_('price',conf.events[0].name)

def test_split():
    eq_([''],event.splitEventString(''))
    eq_(['a'],event.splitEventString('a'))
    eq_(['a','b'],event.splitEventString('a,b'))
    eq_(['a,b'],event.splitEventString('a\\,b'))
    eq_(['a\\b'],event.splitEventString('a\\\\b'))
    eq_(['a\\b','c'],event.splitEventString('a\\\\b,c'))
