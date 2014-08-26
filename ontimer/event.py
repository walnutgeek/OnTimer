'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import IntEnum,Enum
import yaml
import json
from . import OnTime
from . import utils
import datetime
import sys

global_config={}

def joinEnumsIndices(e,meta): 
    return ','.join( str(v.value) for v in e if v.isMetaStatus(meta) )

def joinEnumsIndicesExcept(e,meta): 
    return ','.join( str(v.value) for v in e if not(v.isMetaStatus(meta)) )

def task_vars(task):
    tvars = event_vars(task)
    tvars.update( event_task_id  = int(task['event_task_id']), run = int(task['run_count']) )
    return tvars

def event_vars(event):
    evars = dict(global_config) 
    event_id = int(event['event_id'])
    evars.update( event_id = event_id, event_major = event_id / 100, event_minor = event_id % 100 )
    return evars

def findEnum(enum,v):
    for e in list(enum):
        if e.value == v or e.name == v:
            return e
    raise ValueError('cannot find %r enum in %r ' % ( v, list(enum) ) )

class MetaStates(IntEnum):
    all = 0
    final = 1
    active = 2
    ready = 3
    
class EventStatus(IntEnum):
    active = 1
    fail = 3
    paused = 11
    success = 101
    skip = 102
    
    def isMetaStatus(self,meta): return [True,self.value > 100,self.value <= 10 , self.value <= 10][meta]
    
class TaskStatus(IntEnum):
    scheduled = 1
    running = 2
    fail = 3
    retry = 4
    paused = 11
    success = 101
    skip = 102

    def isMetaStatus(self,meta): return [True,self.value > 100,self.value <= 10, self in (TaskStatus.scheduled,TaskStatus.retry) ][meta]
    
class RunOutcome(IntEnum):
    fail = 3
    success = 101
    skip = 102

    def isMetaStatus(self,meta): return [True,self.value > 100,self.value <= 10, self.value <= 10][meta]
    
class VarTypes(Enum):
    STR = (lambda s: s,      
           lambda s: str(s))
    INT = (lambda s: int(s), 
           lambda i: str(i))
    FLOAT = (lambda s: float(s), 
             lambda f: str(f))
    DATETIME = (lambda s: utils.toDateTime(s,utils.all_formats),
                lambda dt: dt.strftime(utils.format_Y_m_d_H_M_S))
    
    def toValue(self, s):
        return None if s is None else self.value[0](s)

    def toStr(self, v):
        return None if v is None else self.value[1](v) 

def enum_to_map(enum):
    return { e.name: e.value for e in list(enum)} 

def get_meta():
    return {  'MetaStates' : enum_to_map(MetaStates),
            'EventStatus' : enum_to_map(EventStatus),
            'TaskStatus' : enum_to_map(TaskStatus) }
            

class Config:
    def __init__(self,s):
        y = yaml.load(s)
        self.events = [EventType(e) for e in y.pop('events') ]
        self.globals = y.pop('globals')

        if len(y) > 0:
            raise ValueError("Not supported property: %s" % str(y))
        
    def getTypeByName(self,name):
        for e in self.events:
            if e.name == name:
                return e
        raise ValueError("No such type with name: %s" % name, str(self.events) )
    
class EventType:
    def __init__(self,y):
        self.name = str(y.pop('name'))
        self.vars = [VarDef(v) for v in y.pop('vars')  ]
        generatorsList = y.pop('generators',None) #optional
        self.generators = [ GeneratorDef(g) for g in generatorsList] if generatorsList else []
        self.tasks = [ TaskDef(t) for t in y.pop('tasks')]
        if len(y) > 0:
            raise ValueError("Not supported property: %s" % str(y))

class VarDef:
    def __init__(self, v):
        self.name = str(v.pop('name'))
        self.type = VarTypes[str(v.pop('type'))]
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))

    def toValue(self,s):
        return self.type.toValue(s)

    def toStr(self,v):
        return self.type.toStr(v)

        
class GeneratorDef:
    def __init__(self, v): 
        try:
            self.name = str(v.pop('name'))
            self.on_time = OnTime.fromdict(v.pop('on_time') )
            self.wait_final_stage = bool(v.pop('wait_final_stage'))
            self.vals = v.pop('vals')
        except: 
            raise ValueError("caught error:%r property: %s" % (sys.exc_info() ,str(v)))
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))
    
class TaskDef:
    def __init__(self, v):
        self.name = str(v.pop('name'))
        self.depends_on = v.pop('depends_on', None)
        self.cmd = str(v.pop('cmd'))
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))

def splitEventString(s):
    parts = ['']
    lastpart = 0
    next_is_escaped = False
    for c in s:
        if not(next_is_escaped):
            if c == '\\':
                next_is_escaped = True
                continue
            elif c == ',':
                parts.append('')
                lastpart += 1
                continue
        else:
            next_is_escaped = False
        parts[lastpart] += c
    return parts

def joinEventString(it):
    return ','.join((s.replace('\\','\\\\').replace(',','\\,') for s in it))

class Event:
    def __init__(self, event_type,data_tuple, generator=None, started_dt=None, eta_dt=None):
        self.type = event_type
        self.data = data_tuple
        self.status = EventStatus.active 
        self.generator = generator
        self.started_dt = started_dt or datetime.datetime.utcnow()
        self.eta_dt = eta_dt
        self.event_tasks = None

    @staticmethod
    def fromstring(config,s):
        split = splitEventString(s)
        event_type = config.getTypeByName(split.pop(0))
        if len(event_type.vars) != len(split):
            raise ValueError("event vars %s doesn't match config.vars %s requirements" % (s,str(vars)))
        return Event(event_type,[event_type.vars[i].toValue(v) for i,v in enumerate(split)])
        
    def __str__(self):
        return joinEventString( [self.type.name] + [self.type.vars[i].toStr(v) for i,v in enumerate(self.data)] )

    def __repr__(self): return self.__str__()
    
    def generator_id(self): return self.generator.generator_id if self.generator else None
    
    def tasks(self):
        if self.event_tasks == None:
            self.event_tasks = [EventTask(self,t) for t in self.type.tasks]
        return self.event_tasks
    
    def var_dict(self):
        return dict( ( (vd.name, self.data[i]) for i, vd in enumerate(self.type.vars) ) )
    
class EventTask:
    def __init__(self,event,task,run_at_dt=None):
        self.event = event
        self.task = task
        self.status = TaskStatus.scheduled
        self.run_at_dt = run_at_dt or datetime.datetime.utcnow()
        
    def task_id(self):return self.task.task_id
    def task_name(self):return self.task.name
    def _format_vars(self):
        format_vars=dict(global_config)
        format_vars.update(self.event.var_dict())
        #TODO format_vars.update(self.file_dict())
        return format_vars
        
    def cmd(self): return self.task.cmd.format(**self._format_vars())
    def state(self): return  json.dumps({'cmd':self.cmd()} )
        


