import ontimer.runner
from nose.tools import eq_

def test_parseCmdLine(): 
    l = list(ontimer.runner.parseCmdLine('a b  -c " dkfk dkjgkz" f \'slsls\' ')) 
    eq_( ['a', 'b', '-c', ' dkfk dkjgkz', 'f', 'slsls'] , l )

    
