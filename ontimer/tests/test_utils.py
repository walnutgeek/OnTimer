
from nose.tools import eq_
from .. import utils
import datetime

def test_utc_day_adjusted():
    adjmin=utils.utc_adjusted(hours=-3*24)
    adjhour=utils.utc_adjusted(days=-3)
    eq_(adjhour.year,adjmin.year)
    eq_(adjhour.month,adjmin.month)
    eq_(adjhour.day,adjmin.day)
    eq_(adjhour.hour,adjmin.hour)
    eq_(adjhour.minute,adjmin.minute)
    eq_(adjhour.second,adjmin.second)
