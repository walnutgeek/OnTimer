
"""
This module contains of various utility methods and classes.

Examples on this page assume that you imported ``ontimer.utils``
module content into current namespace. Something like::

    from __future__ import print_function
    from ontimer.utils import * # pollution of namespace. 
    
You should import conservatively only used components instead of ``*`` in real code.
But at this time we are just fooling around. Anyway let's begin.

"""
import datetime
from collections import defaultdict, MutableMapping
from sets import Set


#: date format YYYY-MM-DD hh:mm:ss.nano 
format_Y_m_d_H_M_S_n = '%Y-%m-%d %H:%M:%S.%f'
#: date format YYYY-MM-DD hh:mm:ss 
format_Y_m_d_H_M_S = '%Y-%m-%d %H:%M:%S'
#: date format YYYYMMDD-hhmmss 
format_Ymd_HMS     = '%Y%m%d-%H%M%S'
#: date format YYYYMMDDhhmmss 
format_YmdHMS      = '%Y%m%d%H%M%S'
#: date format YYYY-MM-DD
format_Y_m_d       = '%Y-%m-%d'
#: date format YYYYMMDD
format_Ymd         = '%Y%m%d'

#: all date formats above
all_formats = [format_Y_m_d_H_M_S_n,
               format_Y_m_d_H_M_S,
               format_Ymd_HMS,
               format_YmdHMS,
               format_Y_m_d,
               format_Ymd]

def toDateTime(s,formats=all_formats):
    '''trying all formats in the list to parse string into datatime
    
        >>> toDateTime('2014-10-21')
        datetime.datetime(2014, 10, 21, 0, 0)
        >>> toDateTime('20141021')
        datetime.datetime(2014, 10, 21, 0, 0)
        >>> toDateTime('20141021',(format_Ymd,))
        datetime.datetime(2014, 10, 21, 0, 0)
        >>> toDateTime('2014-10-21',(format_Ymd,))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "./ontimer/utils.py", line 38, in toDateTime
            raise ValueError('Cannot parse "%s", tried %s',s,str(formats))
        ValueError: ('Cannot parse "%s", tried %s', '2014-10-21', "('%Y%m%d',)")
        >>> 
    
    
    '''
    if s is None or isinstance(s,datetime.datetime):
        return s
    for f in formats:
        try:
            return datetime.datetime.strptime(s, f)
        except:
            pass
    raise ValueError('Cannot parse "%r", tried %r' % (s,formats))

def utc_adjusted(now = None, **kwargs):
    ''' return utc adjusted. Adjustments should follow conventions 
        of  `datetime.timedelta` .
    
        >>> utc_adjusted()
        datetime.datetime(2014, 10, 22, 6, 19, 12, 73972)
        >>> utc_adjusted(hours=-5)
        datetime.datetime(2014, 10, 22, 1, 19, 28, 120858)
        >>> import datetime
        >>> datetime.datetime.utcnow()
        datetime.datetime(2014, 10, 22, 6, 19, 59, 24108)
        >>>
    
    '''
    now = now or datetime.datetime.utcnow()
    return (now+datetime.timedelta(**kwargs))

def quict(**kwargs): 
    ''' 
    quick way to create dict():
    
    >>> quict( a = 'b', b = 'c')
    {'a': 'b', 'b': 'c'}
    '''
    return kwargs


class KeyEqMixin:
    '''
    add implementation of equality, non-equality and hash to object.
    assumes that subclass implements ``__key__()`` method.
    '''
    def __hash__(self):
        return hash(self.__key__())
    def __eq__(self,other):
        return self.__key__() == other.__key__()
    def __ne__(self,other):
        return self.__key__() != other.__key__()

class KeyCmpMixin(object):
    '''
    add implementation of compare operators: less, greater and etc to object.
    assumes that subclass implements ``__key__()`` method.
    '''
    def __lt__(self, other):
        return self.__key__() < other.__key__()

    def __gt__(self, other):
        return other < self

    def __le__(self, other):
        return not (other < self)

    def __ge__(self, other):
        return not (self < other)

def safe_append(obj,key,val_to_append):
    '''
    ensure that ``list`` created in dictionary and before value append value to that list. Method useful 
    when you have no control over dictionary creation, if you do you may be better off using ``defaultdict(list)``.
    
    >>> x={}
    >>> safe_append(x,'a',5)
    >>> x
    {'a': [5]}
    >>> safe_append(x,'a',7)
    >>> x
    {'a': [5, 7]}
    >>> safe_append(x,'u',2)
    >>> x
    {'a': [5, 7], 'u': [2]}
    >>> 
    '''
    if key in obj:
        obj[key].append(val_to_append)
    else:
        obj[key]=[val_to_append]
 
def flatten_links(object_dict,key, direction):
    '''
    return set of keys that linked to ``key`` provided:
      * ``object_dict`` - dictionary of objects by key
      * ``key`` - key of the object which links needed to be inspected.
      * ``direction`` -  is name of property inside of object that pointed to set of keys of linked objects. 

    >>> x={
    ...    1:{'link':[2,3]},
    ...    2:{'link':[4,5]},
    ...    3:{'link':[5,7]},
    ...    4:{'link':[6]},
    ...    5:{'link':[6,7]},
    ...    6:{'link':[7]},
    ...    7:{},
    ... }
    >>> flatten_links(x,4,'link')
    Set([6, 7])
    >>> flatten_links(x,1,'link')
    Set([2, 3, 4, 5, 6, 7])
    >>> flatten_links(x,2,'link')
    Set([4, 5, 6, 7])
    >>> flatten_links(x,2,'zink')
    Set([])
    >>> 

  
    '''
    visited=Set()
    def _object(visited,key):
        obj = object_dict[key]
        if direction in obj:
            follow_keys = obj[direction]
            for fkey in follow_keys:
                if fkey not in visited:
                    visited.add(fkey)
                    _object(visited,fkey)
    _object(visited, key)
    return visited

def broadcast(it, *args, **kwargs):
    ''' 
    call every element of collection ``it``
    as function with parameters:
    
    >>> lambdas=[lambda x: print( " l1 %r " % x ) ,lambda x: print( " l2 %r " % x )]
    >>> broadcast(lambdas, '1')
     l1 '1' 
     l2 '1' 
    >>> broadcast(lambdas, 2)
     l1 2 
     l2 2 
    >>> broadcast(lambdas, 'three')
     l1 'three' 
     l2 'three' 
    >>> 

    '''
    for callback  in it:
        callback(*args,**kwargs)

class Broadcast:
    '''
    constructor takes ``f`` function as argument, that supposed to return iterator of functions.
    Every time when  when ``call_all(...)`` executed, ``f()`` get called to obtain 
    iterator and all functions from this iterator get called with argument provided to 
    ``call_all``.
    
    >>> def f():
    ...   yield lambda x: print( " l1 %s " % x )
    ...   yield lambda x: print( " l2 %s " % x )
    ... 
    >>> b = Broadcast(f)
    >>> b.call_all('hello')
     l1 hello 
     l2 hello 
    >>> 
        
    '''
    def __init__(self, f):
        self.f = f

    def call_all(self, *args, **kwargs):
        '''
        call all functions with arguments provided: ``(*args,**kwargs)``
        '''
        broadcast(self.f(), *args,**kwargs)

class BroadcastList(list,Broadcast):
    '''
    list of functions to be able to call all these functions at once:
    
    >>> bcast = BroadcastList() 
    >>> bcast.append( lambda x: print( " l1 %s " % x ) )
    >>> bcast.append( lambda x: print( " l2 %s " % x ) )
    >>> bcast.call_all('hello')
     l1 hello 
     l2 hello 
    >>> 
    
    Class inherit all it's methods from `list`, `Broadcast`
    
    '''
    def __init__(self, callback=None):
        list.__init__(self)
        Broadcast.__init__(self, lambda: self)
        if callback is not None:
            self.append(callback)


class ProtectedDict(MutableMapping):
    '''
    Dictionary that restricts access to: update and delete operations
    '''
    def __init__(self, store, update=False, delete=False):
        '''
        * ``store``: dictionary to be protected. 
        * ``update``: *boolean*  True will allow update.
        * ``delete``: *boolean*  True will allow delete.
        
        >>> d={'a':'b', 'b':'c'}
        >>> d
        {'a': 'b', 'b': 'c'}
        >>> pd=ProtectedDict(d)
        >>> pd['x']='y'
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "./ontimer/utils.py", line 162, in __setitem__
            raise ValueError("__setitem__ not allowed: (k,v)=(%r,%r)" % ( key,value))
        ValueError: __setitem__ not allowed: (k,v)=('x','y')
        >>> pd=ProtectedDict(d,True,False)
        >>> pd['x']='y'
        >>> d
        {'a': 'b', 'x': 'y', 'b': 'c'}
        >>> pd
        {'a': 'b', 'x': 'y', 'b': 'c'}
        >>> del pd['x']
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "./ontimer/utils.py", line 168, in __delitem__
            raise ValueError("__delitem__ not allowed: k=%r" % key )
        ValueError: __delitem__ not allowed: k='x'
        >>> pd
        {'a': 'b', 'x': 'y', 'b': 'c'}
        >>> pd=ProtectedDict(d,True,True)
        >>> del pd['x']
        >>> pd
        {'a': 'b', 'b': 'c'}
        >>> 
        '''
        self.store = store
        self._access=(update,delete)
        
    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        if self._access[0]:
            self.store[key] = value
        else:
            raise ValueError("__setitem__ not allowed: (k,v)=(%r,%r)" % ( key,value))

    def __delitem__(self, key):
        if self._access[1]:
            del self.store[key]
        else:
            raise ValueError("__delitem__ not allowed: k=%r" % key )

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __str__(self):
        return self.store.__str__()
    def __repr__(self):
        return self.store.__repr__()
            
class NiceDict(MutableMapping):
    '''
    Dictionary that nice enough to notify if it changed. 
    
    
    '''
    def __init__(self, dictId = None, defvalue=None, onset=None, ondelete=None, onempty=None):
        '''
        * ``dictId``: to help find this dictionary in parent storage. 
          Likely use case is for this NiceDict dictionary to be in parent 
          dictionary it can hold its own key in ``dictId`` variable. 
        * ``defvalue``: *optional*  default value constructor - ``function(key): value`` 
          that will be called every time when not existent element trying to be accessed, 
          expeced to return new value for a key.  ``(key, value)`` pair will be stored  
          in dictionary and ``value`` returned to caller. If function is 
          not defined ``KeyError`` will be raised on non-existent keys.
          
            >>> nd = NiceDict("d1", defvalue=lambda k: 'val of %r' % k )
            >>> nd
            {}
            >>> nd['33']
            "val of '33'"
            >>> nd['abc']
            "val of 'abc'"
            >>> nd
            {'33': "val of '33'", 'abc': "val of 'abc'"}
            >>> 
            
        * ``onset`` : *optional* ``function(nd,key,value)`` will called every time 
          when element set. ``nd`` is dictionary itself.
        * ``ondelete`` : *optional* ``function(nd,key,value)`` will be called every 
          time when element deleted.
        * ``onempty`` : *optional*  ``function(nd)`` will called every time when 
          last element from dictionary deleted and it is empty:
         
            >>> nd = NiceDict("d1", 
            ...   onset=lambda nd,k,v:    print( '-set-',   nd.dictId, k, v), 
            ...   ondelete=lambda nd,k,v: print( '-del-',   nd.dictId, k, v), 
            ...   onempty=lambda nd:      print( '-empty-', nd.dictId) ) 
            >>> nd['a']='b'
            -set- d1 a b
            >>> nd['b']='c'
            -set- d1 b c
            >>> del nd['a']
            -del- d1 a b
            >>> del nd['b']
            -del- d1 b c
            -empty- d1

        '''
        self.dictId = dictId
        self.store = dict()
        self.defvalue=defvalue
        self.onset_bcast = BroadcastList(onset)
        self.ondelete_bcast = BroadcastList(ondelete)
        self.onempty_bcast = BroadcastList(onempty)
        
    def __getitem__(self, key):
        k = self.__keytransform__(key)
        if k not in self.store and self.defvalue:
            v = self.defvalue(k)
            self.store[k]=v
            self.onset_bcast.call_all(self,k,v)
        return self.store[k]

    def __setitem__(self, key, value):
        k = self.__keytransform__(key)
        self.store[k] = value
        self.onset_bcast.call_all(self,k,value)

    def __delitem__(self, key):
        k = self.__keytransform__(key)
        if k in self.store:
            v = self.store[k]
            del self.store[k]
            self.ondelete_bcast.call_all(self, k, v)
            if len(self.store) == 0:
                self.onempty_bcast.call_all(self)

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
    def __str__(self):
        return self.store.__str__()
    def __repr__(self):
        return self.store.__repr__()
        
        
def pass_thru_transformation(data): 
    ''' returns same input ``data`` as output'''    
    return data

class Propagator:
    '''    
    data update will propagate to callback, 
    only if data actually changed:
    
    
    >>> p=Propagator(lambda x: print("x=",x))
    >>> p.update(3)
    x= 3
    True
    >>> p.data , p.last_ts
    (3, datetime.datetime(2014, 11, 4, 16, 14, 40, 822682))
    >>> p.add_callback(lambda y:print("y=",y))
    y= 3
    >>> p.update(3)
    False
    >>> p.update(5)
    x= 5
    y= 5
    True
    >>> p.data , p.last_ts
    (5, datetime.datetime(2014, 11, 4, 16, 18, 50, 74680))
    >>> p.broadcast
    [<function <lambda> at 0x10062e758>, <function <lambda> at 0x10062e6e0>]
    >>> del p.broadcast[1]
    >>> p.update(6)
    x= 6
    True
    >>> 


    
    '''
    def __init__(self, callback=None, broadcast=None, transformation=pass_thru_transformation): 
        if callback and broadcast:
            raise ValueError('callback and broadcast cannot be defined together')
        self.broadcast = BroadcastList() if broadcast is None else broadcast  #: list to store all callback methods
        if callback is not None:
            self.broadcast.append(callback)
        self.transformation = transformation
        self.data = None #: data stored after last successful updates
        self.last_ts = None #: time of last successful update
        

    def update(self,data):
        '''   
        push new ``data`` to propagate to ``callbacks``
        
        returns ``True`` if ``data`` was propagated  
        '''
        transform = self.transformation(data)
        if self.data != transform:
            self.last_ts = datetime.datetime.utcnow()
            self.data = transform
            self.broadcast.call_all(transform)
            return True
        return False
    
    def update_latest_data(self,callback):
        if self.last_ts:
            callback(self.data)

    def add_callback(self,callback):
        if isinstance(self.broadcast, BroadcastList):
            self.broadcast.append(callback)
            self.update_latest_data(callback)
        else:
            raise ValueError("don't know how to append to that broadcast")

class ABDict:
    ''' 
    ABDict - is two level dictionary.  Two levels named: ``A`` and ``B``. 
    Therefore keys  are: ``akey`` and ``bkey``.
     
    It allow to store ``ab_value`` for each unique combination 
    ``akey`` and ``bkey``. Additionaly you may want store : ``a_value`` one for each ``akey``, or 
    ``b_value`` one for each bkey. 
    All these values could be created automatically if appropriate default factory 
    defined on instance creation. 
    
    
    ``ABDict`` does not adhere to ``dict()`` interface, rather contains 4 dictionaries that 
    synchronized between themself:
    
    * ``d.akeys[bkey]`` -> set akeys that defined in for bkey  - actions: ``read``
    * ``d.a[akey]`` -> ``a_value`` - access: ``read``, ``update``
    * ``d.b[akey]`` -> ``b_value`` - access: ``read``, ``update``
    * ``d.ab[akey][bkey]`` -> ab_value - access: ``read``, ``update``, ``delete`` 

    ``d.a``, ``d.b`` automaticaly extend or shink as ``akey``  or ``bkey``   
    introduced or removed in/from ``d.ab``. Because ``d.a`` ,and ``d.b`` are `NiceDict`  
    instances, so you can subscribe on changes in them.
    
    >>> d=ABDict(a_value_factory=lambda akey: 'akey %r' % akey,
    ... b_value_factory=lambda akey: 'bkey %r' % akey,
    ... ab_value_factory=lambda akey,bkey: 'akey %r , bkey %r' % (akey,bkey))
    >>> d.ab[3]['x']
    "akey 3 , bkey 'x'"
    >>> d.ab[5]['x']='something else'
    >>> d.ab[3]['y']
    "akey 3 , bkey 'y'"
    >>> d.ab[3]['z']
    "akey 3 , bkey 'z'"
    >>> d.ab[4]['z']
    "akey 4 , bkey 'z'"
    >>> d.ab[5]['z']
    "akey 5 , bkey 'z'"
    >>> d.ab
    {3: {'y': "akey 3 , bkey 'y'", 'x': "akey 3 , bkey 'x'", 'z': "akey 3 , bkey 'z'"}, 
     4: {'z': "akey 4 , bkey 'z'"}, 5: {'x': 'something else', 'z': "akey 5 , bkey 'z'"}}
    >>> d.a
    {3: 'akey 3', 4: 'akey 4', 5: 'akey 5'}
    >>> d.b
    {'y': "bkey 'y'", 'x': "bkey 'x'", 'z': "bkey 'z'"}
    >>> d.akeys
    defaultdict(<class 'sets.Set'>, {'y': Set([3]), 'x': Set([3, 5]), 'z': Set([3, 4, 5])})
    
    You can override default ``a_value``:
    
    >>> d.a[4]='another value'
    >>> d.a
    {3: 'akey 3', 4: 'another value', 5: 'akey 5'}
    
    You can delete single ``ab_value`` for unique combination ``akey`` and ``bkey``:
    
    >>> del d.ab[3]['x']
    >>> d.ab
    {3: {'y': "akey 3 , bkey 'y'", 'z': "akey 3 , bkey 'z'"}, 4: {'z': "akey 4 , bkey 'z'"}, 
     5: {'x': 'something else', 'z': "akey 5 , bkey 'z'"}}
    >>> d.b
    {'y': "bkey 'y'", 'x': "bkey 'x'", 'z': "bkey 'z'"}
    
    If you want to delete all entries with given ``akey``, 
    you cannot delete whole 2nd level dictionary. Rather you 
    have to use `delete_by_akey` method:
    
    >>> del d.ab[3]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "./ontimer/utils.py", line 221, in __delitem__
        raise ValueError("__delitem__ not allowed: k=%r" % key )
    ValueError: __delitem__ not allowed: k=3
    >>> d.delete_by_akey(3)
    >>> d.ab
    {4: {'z': "akey 4 , bkey 'z'"}, 5: {'x': 'something else', 'z': "akey 5 , bkey 'z'"}}
    >>> d.b
    {'x': "bkey 'x'", 'z': "bkey 'z'"}
    >>> d.a
    {4: 'another value', 5: 'akey 5'}
    
    Also  there is simular method to delete all entries with given ``bkey``:
    
    >>> d.delete_by_bkey('z')
    >>> d.ab
    {5: {'x': 'something else'}}
    >>> d.a
    {5: 'akey 5'}
    >>> d.b
    {'x': "bkey 'x'"}
    >>> d.akeys
    defaultdict(<class 'sets.Set'>, {'x': Set([5])})
    >>> 

    '''
    def __init__(self, a_value_factory = None, b_value_factory=None, ab_value_factory=None):

        def onempty_B(d):
            akey = d.dictId
            del self._ab[akey]
            if akey in self.a:
                del self.a[akey]

        def onset_B(d, bkey ,v):
            akey = d.dictId
            if v is None and ab_value_factory is not None:
                d.store[bkey] = ab_value_factory(akey,bkey)
            self._inverse[bkey].add(akey)
            if b_value_factory is not None and bkey not in self.b:
                self.b[bkey]=b_value_factory(bkey)

        def ondelete_B(d, bkey, v):
            akey = d.dictId
            s=self._inverse[bkey]
            s.remove(akey)
            if len(s)==0:
                del self._inverse[bkey]  
                if bkey in self.b:
                    del self.b[bkey]  

        def onset_A(d,akey,v):
            if a_value_factory is not None and akey not in self.a:
                self.a[akey]=a_value_factory(akey)

        def defvalue_A(akey):
            return NiceDict(dictId=akey,
                            defvalue=lambda bkey: None, 
                            onset=onset_B, 
                            ondelete=ondelete_B,
                            onempty=onempty_B ) 
        
        self._inverse = defaultdict(Set)
        self.akeys = ProtectedDict(self._inverse)
        self.a = NiceDict()
        self.b = NiceDict()
        self._ab = NiceDict(defvalue=defvalue_A, onset=onset_A )
        self.ab = ProtectedDict(self._ab)
    
    def delete_by_akey(self, akey):
        ''' Delete all entries with given ``akey`` '''
        if akey in self._ab:
            bkeys = list(self._ab[akey].keys())
            for bkey in bkeys:
                del self._ab[akey][bkey]
        
    def delete_by_bkey(self, bkey):
        ''' Delete all entries with given ``bkey`` '''
        if bkey in self.akeys:
            akeys = list(self.akeys[bkey])
            for akey in akeys:
                del self.ab[akey][bkey]

def find_enum(enum,v):
    '''
    Find enum by name or by value (value is index in ``IntEnum``) or by itself. 
    Method raise `ValueError` if enum class does not contain given name, value, 
    nor such enum instance.  
    '''
    for e in enum:
        if e == v or e.value == v or e.name == v:
            return e
    raise ValueError('cannot find %r enum in %r ' % ( v, list(enum) ) )

def enum_to_map(enum):
    ''' convert enum to dict '''
    return { e.name: e.value for e in list(enum)} 

def gen_doc_for_enums(*args):
    '''Method generate docs strings for enums. Pass any number of enum classes, 
    all of them will be have ``__doc__`` appended with list of enum constants.
    '''
    for enum in args:
        enum.__doc__ = ( enum.__doc__ if enum.__doc__ else '' ) +  ' , '.join(sorted('``%s``' % e.name for e in enum))

def platform_info():
    '''
    Collect information about platform in one dictionary.
    
    >>> from ontimer import utils
    >>> utils.platform_info()
    {'node': 'Sergeys-MacBook-Pro.local', 'python_version': '2.7.8', 
     'python_implementation': 'CPython', 'system': 'Darwin', 
     'machine': 'x86_64', 'release': '13.4.0', 'processor': 'i386'}
    >>> 

    '''
    import platform
    properties = ['machine','node','processor','python_version','python_implementation','system','release']
    return { k: getattr(platform, k)() for k in properties}

