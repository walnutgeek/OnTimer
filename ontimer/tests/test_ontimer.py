
from nose.tools import eq_
from .. import OnExp, OnState, OnTime
import datetime
from collections import defaultdict

def dt2s(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    
def test_one_date():
    exp = OnExp("0 6 1,31 * tue,wed")
    st = exp.state(datetime.datetime(2014,6,13,0,0,0))
    #rules = exp.rules[schepy._MONTH_DAY][2014]
    eq_(str(st), "2014-07-01 06:00:00")

def test_all_dates():
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
    
    
def test_ontime():
    ont = OnTime("0 6 1,31 * tue,wed","Australia/Sydney")
    s = ont.state(datetime.datetime(2014,7,4,0,0,0))
    eq_("2014-09-30 20:00:00 UTC+0000", dt2s(ont.toUtc(s))) 
    eq_("2014-06-30 20:00:00 UTC+0000", dt2s(ont.toUtc(s.back())) )
    eq_("2014-12-30 19:00:00 UTC+0000", dt2s(ont.toUtc(s.forward())) )
    
    
    
    
