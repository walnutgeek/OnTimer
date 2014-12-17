
from nose.tools import eq_
from .. import utils
import datetime

def expectError(err, action):
    see_err = False
    try: 
        action()
    except err:
        see_err = True
    eq_(see_err,True)

def test_utc_day_adjusted():
    adjmin=utils.utc_adjusted(hours=-3*24)
    adjhour=utils.utc_adjusted(days=-3)
    eq_(adjhour.year,adjmin.year)
    eq_(adjhour.month,adjmin.month)
    eq_(adjhour.day,adjmin.day)
    eq_(adjhour.hour,adjmin.hour)
    eq_(adjhour.minute,adjmin.minute)
    eq_(adjhour.second,adjmin.second)

def test_toDateTime():
    dt=datetime.datetime(2014,10,10)
    eq_(utils.toDateTime(dt),dt)
    expectError(ValueError, lambda: utils.toDateTime('abc'))

def test_quict():
    eq_( { 'x':5}, utils.quict(x = 5 ))

def test_mixins():
    class MyInt(utils.KeyEqMixin,utils.KeyCmpMixin):
        def __init__(self,i):
            self.i = i
        def __key__(self): 
            return self.i
    a = MyInt(1)
    b = MyInt(2)
    x = {}
    x[a] = b
    eq_( a == b , False)
    eq_( a != b , True)
    eq_( a > b , False)
    eq_( a < b , True)
    eq_( a <= b , True)
    eq_( a >= b , False)

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
    

def test_ProtectedDict():
    i = 0
    pd = utils.ProtectedDict({2:5})
    try:
        pd[3]=4
    except ValueError:
        i+=1
    eq_(1,i)
    try:
        del pd[2]
    except ValueError:
        i+=1
    eq_(2,i)
    pd = utils.ProtectedDict({},True,True)
    pd[3]=4
    eq_(pd[3],4)
    eq_(len(pd),1)
    eq_(repr(pd),'{3: 4}' )
    eq_(list(pd.iterkeys()),[3] )
    del pd[3]
    eq_(len(pd),0)
    
    
    
    
    
def test_propagator():
    arr = []
    p=utils.Propagator(lambda x: arr.append(x))
    p.update(5)
    eq_(5,arr[-1])
    eq_(1,len(arr))
    p.update(5)
    eq_(1,len(arr))
    p.update(6)
    eq_(6,arr[-1])
    eq_(2,len(arr))
    p.update(6)
    eq_(6,arr[-1])
    eq_(2,len(arr))
    p.update(6)
    eq_(6,arr[-1])
    eq_(2,len(arr))
    p.update(7)
    eq_(7,arr[-1])
    eq_(3,len(arr))
    p.update(7)
    eq_(7,arr[-1])
    eq_(3,len(arr))
    p.update(7)
    eq_(7,arr[-1])
    eq_(3,len(arr))
    p.update(7)
    eq_(7,arr[-1])
    eq_(3,len(arr))
    arr2=[]
    p.add_callback(lambda x: arr2.append(x))
    eq_(7,arr2[-1])
    eq_(1,len(arr2))
    p2=utils.Propagator(broadcast=utils.Broadcast(lambda:[]))
    expectError(ValueError, lambda: p2.add_callback(lambda x: None))
    expectError(ValueError, lambda: utils.Propagator(callback=lambda:None, broadcast=utils.Broadcast(lambda:[])) )


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
    
def test_safe_append():
    x={}
    utils.safe_append(x,'a',5)
    eq_("{'a': [5]}",str(x))
    utils.safe_append(x,'a',7)
    eq_("{'a': [5, 7]}",str(x))
    utils.safe_append(x,'u',2)
    eq_("{'a': [5, 7], 'u': [2]}",str(x))
    
def test_flatten_links():
    x={
       1:{'link':[2,3]},
       2:{'link':[4,5]},
       3:{'link':[5,7]},
       4:{'link':[6]},
       5:{'link':[6,7]},
       6:{'link':[7]},
       7:{},
    }
    eq_("Set([6, 7])",str(utils.flatten_links(x,4,'link')))
    eq_("Set([2, 3, 4, 5, 6, 7])",str(utils.flatten_links(x,1,'link')))
    eq_("Set([4, 5, 6, 7])",str(utils.flatten_links(x,2,'link')))
    eq_("Set([])",str(utils.flatten_links(x,2,'zink')))
    
def test_Miscellaneous():
    eq_(len(utils.platform_info()),7)
    
def test_Broadcast():
    acc = ['','','','']
    def append0(s):
        acc[0] += s
    def append1(s):
        acc[1] += s
    def append2(s):
        acc[2] += s
    def append3(s):
        acc[3] += s
    def generator1():
        yield append0
        yield append1
    def generator2():
        yield append2
        yield append3
    def generator3():
        yield append0
        yield append3
    def generator4():
        return [append2]
    def generator5():
        yield append1
        yield append2
    def generator6():
        yield append0
        yield append1
        yield append2
        yield append3
    
    utils.Broadcast(generator1).call_all("Hello")
    utils.Broadcast(generator2).call_all("Privet")
    eq_(str(acc),"['Hello', 'Hello', 'Privet', 'Privet']")
    utils.Broadcast(generator3).call_all(" John")
    utils.Broadcast(generator4).call_all(" sto")
    utils.Broadcast(generator5).call_all(" let")
    utils.Broadcast(generator6).call_all("!")
    eq_(str(acc),"['Hello John!', 'Hello let!', 'Privet sto let!', 'Privet John!']" )

from enum import IntEnum,Enum

def test_enums():
    class GeneratorStatus(IntEnum):
        'Choices are:'
        unset = 0 
        running = 2 
        paused = 11  
        ontime = 20
        
    class VarTypes(Enum):
        STR = (lambda s: s,      
               lambda s: str(s))
        INT = (lambda s: int(s), 
               lambda i: str(i))
        FLOAT = (lambda s: float(s), 
                 lambda f: str(f))
        DATETIME = (lambda s: utils.toDateTime(s,utils.all_formats),
                    lambda dt: dt.strftime(utils.format_Y_m_d_H_M_S))
    utils.gen_doc_for_enums(VarTypes,GeneratorStatus)
    
    eq_(GeneratorStatus.__doc__,'Choices are:``ontime`` , ``paused`` , ``running`` , ``unset``')
    
    eq_(VarTypes.__doc__,'``DATETIME`` , ``FLOAT`` , ``INT`` , ``STR``' )
    
    def expectValueError(e, *args):
        i=0
        for a in args:
            try: 
                utils.find_enum(e, a)
            except ValueError:
                i+=1
        return i == len(args)
    
    eq_(True, expectValueError(GeneratorStatus, 'STR', 17, VarTypes.INT))
    eq_(True, expectValueError(VarTypes, 'STR_', 17, GeneratorStatus.unset))

    eq_(GeneratorStatus.paused,utils.find_enum(GeneratorStatus, GeneratorStatus.paused))
    eq_(GeneratorStatus.paused,utils.find_enum(GeneratorStatus, 'paused'))
    eq_(GeneratorStatus.paused,utils.find_enum(GeneratorStatus, 11))
    
    eq_(VarTypes.STR,utils.find_enum(VarTypes, VarTypes.STR))
    eq_(VarTypes.INT,utils.find_enum(VarTypes, 'INT'))
    
    
    
                
        
   
    