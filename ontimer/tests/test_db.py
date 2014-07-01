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
    from ontimer.db import create_db, connect_db
    conn = connect_db(test_dir,filename="test.db")
    eq_(1, list(conn.execute('pragma foreign_keys'))[0][0])
    create_db(conn)
    #raise Exception(os.path.abspath("."))


