import os
import shutil
import unittest

from nose.tools import eq_
from collections import defaultdict
import sqlite3


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()

class TestTest(unittest.TestCase):

    def test_parseCmdLine(self):
        import ontimer.runner
        l = list(ontimer.runner.parseCmdLine('a b  -c " dkfk dkjgkz" f \'slsls\' ')) 
        eq_( ['a', 'b', '-c', ' dkfk dkjgkz', 'f', 'slsls'] , l )

    
