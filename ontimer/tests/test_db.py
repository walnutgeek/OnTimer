import os
import shutil
import unittest

from nose.tools import eq_,with_setup
from .. import OnExp, OnState, event
from collections import defaultdict


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()

test_dir = os.path.abspath("test-out")
if os.path.isdir(test_dir):
    shutil.rmtree(test_dir)
os.mkdir(test_dir)
c1_text = open("ontimer/tests/test-config.yaml","r").read()
c2_text = open("ontimer/tests/test-config-v2.yaml","r").read()

def test_dbcreation():
    from ontimer.db import Dao
    dao = Dao(test_dir,filename="test.db")
    eq_(1, dao.query('pragma foreign_keys')[0][0])
    dao.create_db()
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
    
    
    #raise Exception(os.path.abspath("."))


