import os
import shutil
import unittest

from nose.tools import eq_
from .. import OnExp, OnState
import datetime
from collections import defaultdict
import sqlite3


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()

class TestTest(unittest.TestCase):

    def test_one_date(self):
        exp = OnExp("0 6 1,31 * tue,wed")
        st = exp.state(datetime.datetime(2014,6,13,0,0,0))
        print st
        #rules = exp.rules[schepy._MONTH_DAY][2014]
        eq_(str(st), "2014-07-01 06:00:00")

    def test_all_dates(self):
        exp = OnExp("0 6 1,31 * tue,wed")
        s = exp.state(datetime.datetime(1000,1,1,0,0,0))
        dd = defaultdict(list)
        ls = []
        loop=True
        while loop:
            try:
                dt = s.toDateTime()
                dd[dt.year].append(dt)
                ls.append(dt)
                s = s.forward()
            except ValueError,e:
                loop = False
        eq_(len(dd),2000)
        eq_(len(ls)/len(dd),5)
 
    def test_dbcreation(self):
        from ..db import create_db, connect_db
        dir = os.path.abspath("test-out")
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
        conn = connect_db(dir,filename="test.db")
        eq_(1, list(conn.execute('pragma foreign_keys'))[0][0])
        create_db(conn)
        #raise Exception(os.path.abspath("."))
    
