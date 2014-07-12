'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import Enum
import yaml
from . import OnTime
from . import utils
import datetime


class EventStatus(Enum):
    active = 1
    eta_breach = 2 
    success = 3
    skip = 4
    paused = 5
    fail = 101

class TaskStatus(Enum):
    scheduled = 1
    running = 2
    retry = 3
    success = 11
    skip = 12
    fail = 101

class VarTypes(Enum):
    STR = (lambda s: s,      
           lambda s: str(s))
    INT = (lambda s: int(s), 
           lambda i: str(i))
    FLOAT = (lambda s: float(s), 
             lambda f: str(f))
    DATETIME = (lambda s: utils.toDateTime(s,utils.all_formats),
                lambda dt: dt.strptime(utils.format_Y_m_d_H_M_S))
    
    def toValue(self, s):
        return None if s is None else self.value[0](s)

    def toStr(self, v):
        return None if v is None else self.value[1](v) 

class Config:
    def __init__(self,s):
        y = yaml.load(s)
        self.events = [EventType(e) for e in y.pop('events') ]
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
        self.type = getattr(VarTypes,str(v.pop('type')))
        if self.type == 'enum' :
            self.elements = v.pop('elements')
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))

    def toValue(self,s):
        return self.type.toValue(s)

        
class GeneratorDef:
    def __init__(self, v): 
        self.name = str(v.pop('name'))
        self.on_time = OnTime.fromdict(v.pop('on_time') )
        self.wait_final_stage = bool(v.pop('wait_final_stage'))
        self.vals = v.pop('vals')
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))
    
class TaskDef:
    def __init__(self, v):
        self.name = str(v.pop('name'))
        self.depends_on = v.pop('depends_on', None)
        taskType = v.pop('type') 
        self.type = 'ontimer.runner.%s' % taskType 
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

class Event:
    def __init__(self, event_type,data_tuple):
        self.type = event_type
        self.data = data_tuple

    @staticmethod
    def fromstring(config,s):
        split = splitEventString(s)
        event_type = config.getTypeByName(split.pop(0))
        if len(event_type.vars) != len(split):
            raise ValueError("event vars %s doesn't match config.vars %s requirements" % (s,str(vars)))
        return Event(event_type,[type.vars[i].toValue(v) for i,v in enumerate(split)])
        
        