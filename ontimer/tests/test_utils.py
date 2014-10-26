
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

def test_abdict():
    d=utils.ABDict(a_value_factory=lambda akey: 'akey %r' % akey,
        b_value_factory=lambda akey: 'bkey %r' % akey,
        ab_value_factory=lambda akey,bkey: 'akey %r , bkey %r' % (akey,bkey))
    eq_(str(d.ab[3]['x']),"akey 3 , bkey 'x'")
    d.ab[5]['x']='something else'
    eq_(str(d.ab[3]['y']),"akey 3 , bkey 'y'")
    eq_(str(d.ab[3]['z']),"akey 3 , bkey 'z'")
    eq_(str(d.ab[4]['z']),"akey 4 , bkey 'z'")
    eq_(str(d.ab[5]['z']),"akey 5 , bkey 'z'")
    eq_(str(d.ab),'{3: {\'y\': "akey 3 , bkey \'y\'", \'x\': "akey 3 , bkey \'x\'", \'z\': "akey 3 , bkey \'z\'"}, 4: {\'z\': "akey 4 , bkey \'z\'"}, 5: {\'x\': \'something else\', \'z\': "akey 5 , bkey \'z\'"}}')
    eq_(str(d.a),"{3: 'akey 3', 4: 'akey 4', 5: 'akey 5'}")
    eq_(str(d.b), '{\'y\': "bkey \'y\'", \'x\': "bkey \'x\'", \'z\': "bkey \'z\'"}' )
    eq_(str(d.akeys),"defaultdict(<class 'sets.Set'>, {'y': Set([3]), 'x': Set([3, 5]), 'z': Set([3, 4, 5])})" )
    d.a[4]='another value'
    eq_(str(d.a),"{3: 'akey 3', 4: 'another value', 5: 'akey 5'}")
    try:
        del d.ab[3]
        eq_(1,0) #fail
    except ValueError:
        pass
    d.delete_by_akey(3)
    eq_(str(d.ab),'{4: {\'z\': "akey 4 , bkey \'z\'"}, 5: {\'x\': \'something else\', \'z\': "akey 5 , bkey \'z\'"}}')
    eq_(str(d.a), "{4: 'another value', 5: 'akey 5'}")
    eq_(str(d.b), '{\'x\': "bkey \'x\'", \'z\': "bkey \'z\'"}')
    
    d.delete_by_bkey('z')
    eq_(str(d.a),"{5: 'akey 5'}")
    eq_(str(d.b),'{\'x\': "bkey \'x\'"}')
    eq_(str(d.akeys),"defaultdict(<class 'sets.Set'>, {'x': Set([5])})"  )
    

def test_broadcast():
    acc = ['','','','']
    def append0(s):
        acc[0] += s
    def append1(s):
        acc[1] += s
    def append2(s):
        acc[2] += s
    def append3(s):
        acc[3] += s
    utils.broadcast([append0,append1],"Hello")
    utils.broadcast([append2,append3],"Privet")
    eq_(str(acc),"['Hello', 'Hello', 'Privet', 'Privet']")
    utils.broadcast([append0,append3]," John")
    utils.broadcast([append2]," sto")
    utils.broadcast([append1,append2]," let")
    utils.broadcast([append0,append1,append2,append3],"!")
    eq_(str(acc),"['Hello John!', 'Hello let!', 'Privet sto let!', 'Privet John!']" )

    
    