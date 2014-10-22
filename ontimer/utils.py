
"""
This module contains of various utility methods and classes.


"""
import datetime
from collections import defaultdict, MutableMapping


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
all_formats = [format_Y_m_d_H_M_S,
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
          File "/Users/sergeyk/Documents/workspace/OnTimer/ontimer/utils.py", line 38, in toDateTime
            raise ValueError('Cannot parse "%s", tried %s',s,str(formats))
        ValueError: ('Cannot parse "%s", tried %s', '2014-10-21', "('%Y%m%d',)")
        >>> 
    
    
    '''
    if isinstance(s,datetime.datetime):
        return s
    for f in formats:
        try:
            return datetime.datetime.strptime(s, f)
        except:
            pass
    raise ValueError('Cannot parse "%s", tried %s',s,str(formats))

def utc_adjusted(**kwargs):
    ''' return utc adjusted 
    
        >>> utc_adjusted()
        datetime.datetime(2014, 10, 22, 6, 19, 12, 73972)
        >>> utc_adjusted(hours=-5)
        datetime.datetime(2014, 10, 22, 1, 19, 28, 120858)
        >>> import datetime
        >>> datetime.datetime.now()
        datetime.datetime(2014, 10, 21, 23, 19, 59, 24108)
        >>>
    
    '''
    return (datetime.datetime.utcnow()+datetime.timedelta(**kwargs))

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

def broadcast(it, *args, **kwargs):
    ''' 
    call every element of collection ``it``
    as function with parameters
    '''
    for callback  in it:
        callback(*args,**kwargs)

class Broadcast(list):
    '''
    list of functions to be able to call all these functions at once:
    
    >>> bcast = Broadcast() 
    >>> bcast.append( lambda x: print( " l1 %s " % x ) )
    >>> bcast.append( lambda x: print( " l2 %s " % x ) )
    >>> bcast.call_all('hello')
     l1 hello 
     l2 hello 
    >>> 
        
    '''
    def __init__(self, callback=None):
        if callback is not None:
            self.append(callback)

    def call_all(self, *args, **kwargs):
        '''
        call all functions with arguments provided: ``(*args,**kwargs)``
        '''
        broadcast(self, *args,**kwargs)
            
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
        self.onset_bcast = Broadcast(onset)
        self.ondelete_bcast = Broadcast(ondelete)
        self.onempty_bcast = Broadcast(onempty)
        
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
    
    >>> p=Propagator(lambda x: print(x))
    >>> p.update(5)
    5
    >>> p.update(5)
    >>> p.update(6)
    6
    >>> p.update(6)
    >>> p.update(7)
    7
    >>> p.update(7)
    >>> 
    
    '''
    def __init__(self, callback, transformation=pass_thru_transformation): 
        self.callback = callback
        self.transformation = transformation
        self.data = None
        
    def update(self,data):
        '''   push new ``data`` to propagate '''
        transform = self.transformation(data)
        if self.data != transform:
            self.data = transform
            self.callback(transform)




class KeyGroupValue:
    def __init__(self,kval_producer = None):
        self.kval_producer = kval_producer
        self.key_map = {}
        self.key_group_map = {}
        self.inverse = None

    def keys(self):
        return self.key_group_map.keys()

    def kvals(self):
        return self.key_map.values()

    def keys_by_group(self,group):
        return self._inverse()[group]
    
    def get_groups(self, key):
        return self.key_group_map[key]
 
    def contains(self, key, group):
        return key in self.key_group_map and group in self.key_group_map[key]
        
    def get(self, key, group):
        return self.key_group_map[key][group]
    
    def put(self, key, group, value):
        if key not in self.key_group_map:
            self.key_group_map[key]={ group : value }
            if self.kval_producer:
                self.key_map[key]=self.kval_producer(key)
        else:
            self.key_group_map[key][group]=value
        self.inverse = None

    def get_kval(self, key):
        return self.key_map[key]
    
    def has_kval(self, key):
        return key in self.key_map
    
    def set_kval(self, key, kval):
        if key not in self.key_group_map:
            raise KeyError("%r key not in key_group_map" % key)
        self.key_map[key] = kval
        
    def del_kval(self, key):
        del self.key_map[key]
        
    def _inverse(self):
        if None == self.inverse:
            inverse = defaultdict(set)
            for k in self.key_group_map:
                for g in self.key_group_map[k]:
                    inverse[g].add(k)
            self.inverse = inverse
        return self.inverse
        

    def delete_key(self, key):
        del self.key_group_map[key]
        self._delete_key_map_entry(key)
        self.inverse = None

    def delete_key_group(self, key, group):
        self._delete_key_group(key, group)
        self.inverse = None
    
    def delete_group(self, group):
        keys = self.keys_by_group(group)
        for key in keys:
            self._delete_key_group(key, group)
        self.inverse = None
    
    def _delete_key_map_entry(self, key):
        if key in self.key_map: 
            del self.key_map[key]
                
    def _delete_key_group(self, key, group):
        del self.key_group_map[key][group]
        if len(self.key_group_map[key]) == 0:
            del self.key_group_map[key]
            self._delete_key_map_entry(key)
            
        
        
