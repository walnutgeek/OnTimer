from nose.tools import eq_,with_setup
from .. import boss
import sys

def test_boss():
    eq_(len(boss.gen_wordlist()),4) 
    
def test_quickboss():
    savestderr = sys.stderr
    class Devnull(object):
        def write(self, _): pass
    sys.stderr = Devnull()
    try:
        try:
            boss.main(['--delay','0', '--errvsout', '0'])
        except SystemExit:
            pass
        try:
            boss.main(['--delay','0', "--freakout",'2', '--errvsout', '2'])
        except SystemExit:
            pass
    finally:
        sys.stderr = savestderr
       

