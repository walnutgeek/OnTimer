
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

def test_key_group_value():
    kgv = utils.key_group_value()
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k2','g1', 'v2')
    kgv.put('k1','g2', 'v3')
    
    eq_(kgv.get('k1','g1'),'v1')
    eq_(kgv.get('k2','g1'),'v2')
    eq_(kgv.get('k1','g2'),'v3')
    
    try:
        kgv.get('k','g')
        eq_(1,0) #fail
    except KeyError:
        pass
    
    eq_(kgv.keys_by_group('g1'),set(['k1','k2']))
    eq_(kgv.keys_by_group('g2'),set(['k1']))
    eq_(kgv.keys(),['k2', 'k1'])
    
    kgv.delete_key('k1')
    
    eq_(kgv.get('k2','g1'),'v2')
    eq_(kgv.keys_by_group('g1'),set(['k2']))
    eq_(kgv.keys(),['k2'])
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k1','g2', 'v3')
    
    kgv.delete_group('g1')
    
    eq_(kgv.get('k1','g2'),'v3')
    eq_(kgv.keys_by_group('g2'),set(['k1']))
    eq_(kgv.keys(),['k1'])
    eq_(kgv.get_groups('k1'), {'g2': 'v3'})
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k2','g1', 'v2')
    
    kgv.delete_key_group('k1', 'g1')
    eq_(kgv.keys(),['k2', 'k1'])

    kgv.delete_key_group('k1', 'g2')
    eq_(kgv.keys(),['k2'])
    
def test_kval_in_key_group_value():
    kgv = utils.key_group_value(lambda k: k+'_')
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k2','g1', 'v2')
    kgv.put('k1','g2', 'v3')
    
    eq_(kgv.get('k1','g1'),'v1')
    eq_(kgv.get('k2','g1'),'v2')
    eq_(kgv.get('k1','g2'),'v3')
    
    try:
        kgv.get('k','g')
        eq_(1,0) #fail
    except KeyError:
        pass
    
    eq_(kgv.keys_by_group('g1'),set(['k1','k2']))
    eq_(kgv.keys_by_group('g2'),set(['k1']))
    eq_(kgv.keys(),['k2', 'k1'])
    eq_(kgv.get_kval('k2'),'k2_')
    eq_(kgv.get_kval('k1'),'k1_')
    
    kgv.delete_key('k1')
    
    eq_(kgv.get('k2','g1'),'v2')
    eq_(kgv.keys_by_group('g1'),set(['k2']))
    eq_(kgv.keys(),['k2'])
    eq_(kgv.get_kval('k2'),'k2_')
    
    try:
        kgv.get_kval('k1')
        eq_(1,0) #fail
    except KeyError:
        pass
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k1','g2', 'v3')
    
    kgv.delete_group('g1')

    eq_(kgv.get_kval('k1'),'k1_')
    try:
        kgv.get_kval('k2')
        eq_(1,0) #fail
    except KeyError:
        pass
    
    eq_(kgv.get('k1','g2'),'v3')
    eq_(kgv.keys_by_group('g2'),set(['k1']))
    eq_(kgv.keys(),['k1'])
    eq_(kgv.get_groups('k1'), {'g2': 'v3'})
    
    kgv.put('k1','g1', 'v1')
    kgv.put('k2','g1', 'v2')
    
    kgv.delete_key_group('k1', 'g1')
    eq_(kgv.keys(),['k2', 'k1'])

    eq_(kgv.get_kval('k2'),'k2_')
    eq_(kgv.get_kval('k1'),'k1_')
    
    kgv.delete_key_group('k1', 'g2')
    eq_(kgv.keys(),['k2'])

    eq_(kgv.get_kval('k2'),'k2_')
    
    try:
        kgv.get_kval('k1')
        eq_(1,0) #fail
    except KeyError:
        pass

    
    