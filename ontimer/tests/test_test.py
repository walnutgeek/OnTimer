import os
import unittest

from nose.tools import eq_
from .. import OnExp, OnState
import datetime
from collections import defaultdict


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
 
