'''
Created on Jul 11, 2014

@author: sergeyk
'''
import datetime
from collections import defaultdict


format_Y_m_d_H_M_S = '%Y-%m-%d %H:%M:%S'
format_Ymd_HMS     = '%Y%m%d-%H%M%S'
format_YmdHMS      = '%Y%m%d%H%M%S'
format_Y_m_d       = '%Y-%m-%d'
format_Ymd         = '%Y%m%d'

all_formats = [format_Y_m_d_H_M_S,
               format_Ymd_HMS,
               format_YmdHMS,
               format_Y_m_d,
               format_Ymd]

def toDateTime(s,formats=all_formats):
    '''try different date formats to parse string'''
    if isinstance(s,datetime.datetime):
        return s
    for f in formats:
        try:
            return datetime.datetime.strptime(s, f)
        except:
            pass
    raise ValueError('Cannot parse "%s", tried %s',s,str(formats))

def utc_adjusted(**kwargs):
    ''' return utc adjusted '''
    return (datetime.datetime.utcnow()+datetime.timedelta(**kwargs))

def quict(**kwargs): 
    ''' quick way to create dict() '''
    return kwargs


class KeyEqMixin:
    def __hash__(self):
        return hash(self.__key__())
    def __eq__(self,other):
        return self.__key__() == other.__key__()
    def __ne__(self,other):
        return self.__key__() != other.__key__()

class KeyCmpMixin(object):
    def __lt__(self, other):
        return self.__key__() < other.__key__()

    def __gt__(self, other):
        return other < self

    def __le__(self, other):
        return not (other < self)

    def __ge__(self, other):
        return not (self < other)

def broadcast(it, *args, **kwargs):
    for callback  in it:
        callback(*args,**kwargs)


class KeyGroupValue:
    def __init__(self,kval_producer = None):
        self.kval_producer = kval_producer
        self.key_map = {}
        self.key_group_map = {}
        self.inverse = None

    def keys(self):
        return self.key_group_map.keys()

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

    def _delete_key_map_entry(self, key):
        if key in self.key_map: 
                del self.key_map[key]
                
    def _delete_key_group(self, key, group):
        del self.key_group_map[key][group]
        if len(self.key_group_map[key]) == 0:
            del self.key_group_map[key]
            self._delete_key_map_entry(key)
            

    def delete_key_group(self, key, group):
        self._delete_key_group(key, group)
        self.inverse = None
    
    def delete_group(self, group):
        keys = self.keys_by_group(group)
        for key in keys:
            self._delete_key_group(key, group)
        self.inverse = None
    
            
        
        
