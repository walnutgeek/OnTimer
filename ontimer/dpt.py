'''
DPT - Data Propagation tree

path 'u1', 'g2'

'''

from enum import Enum
from . import utils
import json
from collections import defaultdict


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
    
    'e31' - event with ``event_id == 35``
    
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
        return self.letty.value[self.s]

    def timematch(self, rec):
        time = utils.utc_adjusted(days=-self.n)
        for field_name in self.config()['time']:
            if time <= utils.toDateTime(rec[field_name]):
                return True
        return False
    
    def eventmatch(self,rec):
        config = self.config()
        if 'event' in config:
            if rec[config['event']] == self.n:
                return rec
        elif 'task' in config  :  
            tasks = [ t for t in rec['tasks'] if t[config['task'] == self.n ]]
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
        self.elems = []
        while len(s) > 0:
            if s[0].isdigit():
                raise ValueError("s supposed to be not digit char: %s" % s)
            i = 1
            while i < len(s) and s[i].isdigit() : 
                i = i + 1
            self.elems.append(PathElem(s[0],int(s[1:i])))
            s = s[i:]
        if len(self.elems) > 0  and self.elems[0].s == 'r':
            raise ValueError('%r cannot be first PathElem: %r' % ('r',self.elems) )
        if len(self.elems) == 0 or self.elems[0].letty == Letty.event :
            self.elems.insert(0, DEFAULT_TIME_ELEM)
        self.type = self.elems[0].letty
        if len(self.elems) > 2 :
            raise ValueError('path can contain more then 2 elems: %r' % self.elems )
            
    def __str__(self):
        return "".join(self.elems)
 
    def __repr__(self):
        return repr(str(self))
            
    def __key__(self):
        return self.elems
    '''
    '''
    def isdecendant(self,other):
        self._validate_time()
        if len(self.elems) == 1 and self.elems[0].s == 'z' :
            raise ValueError('has to be single z-elem and not: %r', self)
        other._validate_time()
        return self.elems[0].n >= other.elems[0].n 
       
    def _validate_time(self):
        if self.type != Letty.time:
            raise ValueError("filter only can be applied to time type")

    def filter(self, event_data ):
        self._validate_time()
        filtered = []
        for rec in event_data:
            if self.elems[0].timematch(rec) :
                if len(self.elems) == 1 :
                    filtered.append(rec)
                else:
                    match = self.elems[1].eventmatch(rec)
                    if match:
                        filtered.append(match)
        return filtered

DEFAULT_PATH = Path('')

 

class Subscriber:
    def __init__(self, publisher, client ):    
        self.publisher = publisher
        self.client = client
        self.topics = None
        
    def updateClient(self, data):
        self.client.write_message(json.dumps(data))
        
    def updateTopics(self, topics):
        if self.topics != topics :
            self.topics = topics
            self.publisher.subscribe(self)


    
class Publisher():
    '''
    publisher receives all topics that client interested to consume. It detect 
    if these tokens supposed to be subscription or one-of request and routes it 
    to appropriate channel: 
    if request is about tasks an within z31(DEFAULT_PATH), it is added to broadcast
    
    '''
    
    def __init__(self, provider):
        self.provider = provider
        self.time_subscriptions = utils.ABDict(a_value_factory = lambda path: utils.Propagator(callback,transformation=path.filter) ) 
        self.time_propagator = utils.Propagator(lambda data: utils.broadcast(self.time_subscriptions.kvals(), data))
        self.log_subscriptions = utils.KeyGroupValue()
        self.pathcast = defaultdict(dict)
        self.propagator = utils.Propagator(self.broadcast.update)
    
    def check_provider(self):
        self.time_propagator.update(self.provider(DEFAULT_PATH))
    
    def subscribe(self, subscriber):
        for topic in subscriber.topics:
            if DEFAULT_PATH.isdecendant(topic):
                propagator = Propagator(subscriber.updateClient,topic.filter)
                self.broadcast.add_observer(propagator.update,subscriber.client)  
            else:
                if self.provider.islive(topic):
                    self.pathcast[topic]
                subscriber.updateClient(self.provider.getdata(topic))
    

