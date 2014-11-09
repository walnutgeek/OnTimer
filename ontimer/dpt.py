'''
DPT - Data Propagation tree

path 'u1', 'g2'

'''

from enum import Enum
from . import utils
import json
from collections import defaultdict
import itertools


class Letty(Enum):
    ''' 
    ``Letty`` - Type of `PathElem`.
    
    `PathElem` string is defined by ``quality`` (single character) followed by ``quantity`` (number). 
    ``Letty`` help to organize PathElem in group using ``quality`` part. Letty used to to define common behavior 
    for whole group.
    
    Currently defined following Letty's:  
    '''
    time =  { 'vars' : { 'z' : { 'contains': ['u','s'], 'time': ('scheduled_dt','updated_dt') }  , 
                   'u' : { 'time': ('updated_dt') }, 
                   's' : { 'time': ('scheduled_dt') } } } 
    event = { 'vars' : {  'e' : { 'event' : 'event_id' },
                   'E' : { 'event' : 'event_type_id' },
                   'g' : { 'event' : 'generator_id' },
                   't' : { 'task' : 'task_id' },
                   'T' : { 'task' : 'task_type_id' } } }
    log =   { 'vars' : { 'l' : { 'artifact' : 'task_id' } ,
                 'r' : { 'artifact' : 'run' } } }
    
utils.gen_doc_for_enums(Letty)
    
def findLetty(ch):
    ''' find Letty by ``quality`` character '''
    for letty in Letty: 
        if ch in letty.value['vars']:
            return letty
    raise ValueError( '%r does not match any letty:%r' % (ch,[ l.value['vars'].keys() for l in Letty] ) )


     
class PathElem(utils.KeyEqMixin,utils.KeyCmpMixin):
    '''
    ``PathElem`` defined by ``quality`` (single character) and ``quantity`` (number).
    
    For Example:
    
    'e31' - event with ``event_id == 31``
    
    'z7' - all events/tasks scheduled or updated within last 7 days
    
    '''
    def __init__(self,s,n = None):
        if n == None:
            if isinstance( s , basestring ) and len(s) > 1 :
                self.s = s[0:1]
                self.n = int(s[1:])
            else:
                raise ValueError("s supposed to be string with char and number, but it is: %r" % s)
        else:
            if not(isinstance( n , (int,long) )):
                raise ValueError("n supposed to be number, but it is: %r" % n)
            if not(isinstance( s , basestring )) or 1 != len(s) :
                raise ValueError("s supposed to be one char string, but it is: %r" % s)
            self.s = s
            self.n = n
        self.letty = findLetty(self.s)
    
    def __str__(self):
        return "%s%d" % (self.s,self.n)
 
    def __repr__(self):
        return str(self)
            
    def __key__(self):
        return (self.s,self.n)
    
    def config(self):
        return self.letty.value['vars'][self.s]

    def timematch(self, rec, now = None):
        time = utils.utc_adjusted(now=now,days=-self.n) 
        for field_name in self.config()['time']:
            extracted = utils.toDateTime(rec[field_name])
            if extracted is not None and time <= extracted:
                return True
        return False
    
    def eventmatch(self,rec):
        config = self.config()
        if 'event' in config:
            if rec[config['event']] == self.n:
                return rec
        elif 'task' in config  :  
            tasks = [ t for t in rec['tasks'] if t[config['task']] == self.n ]
            if len(tasks):
                rec_copy = rec.copy()
                rec_copy['tasks'] = tasks
                return rec_copy
        return None

#: default element. data for this 
#: element will be retrieved from server regularly
#: and if there is changes, data will be propagated 
#: to all appropriate subscriptions
 
DEFAULT_TIME_ELEM = PathElem('z31') 

class Path(utils.KeyEqMixin,utils.KeyCmpMixin):
    '''
        sequence of 1 or 2 `PathElem` elements. In string 
        representation all elements are 
        concatenated to each other with no delimiters.
        
        If path created with ``Letty.event`` type element. 
        `DEFAULT_TIME_ELEM` will be automatically inserted as first element.

        * ``elems`` - contains all `PathElem` elements
        * ``type`` - `Letty` first element of path
        
        
    '''
    def __init__(self,s):
        if not(isinstance( s , basestring )) :
            raise ValueError("s supposed to be string, but it is: %r" % s)
        elems = []
        while len(s) > 0:
            if s[0].isdigit():
                raise ValueError("s supposed to be not digit char: %s" % s)
            i = 1
            while i < len(s) and s[i].isdigit() : 
                i = i + 1
            elems.append(PathElem(s[0],int(s[1:i])))
            s = s[i:]
        if len(elems) > 0  and elems[0].s == 'r':
            raise ValueError('%r cannot be first PathElem: %r' % ('r',elems) )
        if len(elems) == 0 or elems[0].letty == Letty.event :
            elems.insert(0, DEFAULT_TIME_ELEM)
        self.type = elems[0].letty
        self.elems = tuple(elems)
        if len(self.elems) > 2 :
            raise ValueError('path can contain more then 2 elems: %r' % (self.elems,) )
            
    def __str__(self):
        return "".join(str(e) for e in self.elems)
 
    def __repr__(self):
        return repr(str(self))
            
    def __key__(self):
        return self.elems
 
       
    def isdecendant(self,parent):
        self._validate_time()
        parent._validate_time()
        return len(parent.elems) == 1 and (parent.elems[0].s == 'z' or  parent.elems[0].s == self.elems[0].s) and self.elems[0].n <= parent.elems[0].n 
    
    def get_root(self):
        if self.type == Letty.time and self != DEFAULT_PATH and self.isdecendant(DEFAULT_PATH) :
            return DEFAULT_PATH
        return None
        
    def isroot(self):
        ''' if path  is root of data tree and have to be data has to be requested from `ontimer.db.Dao` '''
        return self.get_root() is None
           
    def _validate_time(self):
        if self.type != Letty.time:
            raise ValueError("filter only can be applied to time type")

    def filter(self, event_data , now=None):
        now = utils.utc_adjusted(now)
        self._validate_time()
        filtered = []
        for rec in event_data:
            if self.elems[0].timematch(rec, now) :
                if len(self.elems) == 1 :
                    filtered.append(rec)
                else:
                    match = self.elems[1].eventmatch(rec)
                    if match:
                        filtered.append(match)
        return filtered

#: default path
DEFAULT_PATH = Path('')

class Publisher():
    '''
    publisher receives all topics that client interested to consume. It detect 
    if these tokens supposed to be subscription or one-of request and routes it 
    to appropriate channel: 
    if request is about tasks an within z31(DEFAULT_PATH), it is added to broadcast
    '''
    
    def __init__(self):
        publisher = self
        class PathValue:
            def __init__(self,path):
                self.publisher = publisher
                self.path=path
                if self.path.isroot():
                    self.cache = utils.Propagator( broadcast=utils.Broadcast(
                        lambda: itertools.chain(self.all_propagator_updates(),self.all_write_messages()) ) )
                else:
                    self.cache = utils.Propagator( broadcast=utils.Broadcast( self.all_write_messages), 
                                                   transformation=self.path.filter )

            def all_write_messages(self):
                return ( c.write_message for c in self.publisher.subscriptions.ab[self.path] if c is not None )
                                                   
            def all_propagator_updates(self):
                return ( pv.cache.update for pv in self.publisher.subscriptions.a.itervalues() 
                        if pv.path.isdecendant(self.path) )
                
        self.subscriptions = utils.ABDict(a_value_factory=PathValue)
        self.subscriptions.ab[DEFAULT_PATH][None]=None
    
    def root_path_iter(self):
        ''' 
        all root paths in publisher. Data  for these path will 
        be regularly requested from `ontimer.db.Dao` 
        '''
        return ( p for p in self.subscriptions.ab if p.isroot() )
    
    def add_client(self,c):
        ''' '''
        def process_paths(paths):
            for p in paths:
                self.subscriptions.ab[p][c]=None
            todelete = [p for p in self.subscriptions.akeys[c] if p not in paths]
            for p in todelete:
                del self.subscriptions.ab[p][c]
                
        c.topics_propagator.add_callback(process_paths)
        
    def publish(self, path, data):
        self.subscriptions.a[path].cache.update(data)
    
    

