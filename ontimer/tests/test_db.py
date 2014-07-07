import os
import shutil
import unittest

from nose.tools import eq_,with_setup
from .. import OnExp, OnState
import datetime
from collections import defaultdict
import sqlite3


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()

test_dir = os.path.abspath("test-out")
if os.path.isdir(test_dir):
    shutil.rmtree(test_dir)
os.mkdir(test_dir)

def test_dbcreation():
    from ontimer.db import Dao
    dao = Dao(test_dir,filename="test.db")
    eq_(1, dao.query('pragma foreign_keys')[0][0])
    dao.create_db()
    eq_(1, len(dao.query('select * from settings')))
    eq_(None,dao.get_config())
    dao.set_config('hello')
    eq_(1,dao.get_config()[0])
    eq_('hello',dao.get_config()[2])
    dao.set_config('hello')
    eq_(1,dao.get_config()[0])
    eq_('hello',dao.get_config()[2])
    eq_('hello',dao.get_config()[2])
    dao.set_config('hello2')
    eq_(2,dao.get_config()[0])
    eq_('hello2',dao.get_config()[2])
    
    
    #raise Exception(os.path.abspath("."))


