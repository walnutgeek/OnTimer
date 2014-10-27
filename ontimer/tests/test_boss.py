from nose.tools import eq_,with_setup
from .. import boss

def test_boss():
    eq_(len(boss.gen_wordlist()),4) 
    
       

