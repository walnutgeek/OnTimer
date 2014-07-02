
from nose.tools import eq_
from .. import event
import datetime
from collections import defaultdict

def test_yaml():
    s = open("ontimer/tests/test-config.yaml","r").read()
    conf = event.Config(s)
    eq_('price',conf.events[0].name)
