'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import Enum
import yaml
from . import OnTime

class EventState(Enum):
    active = 1
    eta_breach = 2 
    success = 3
    skip = 4
    paused = 5
    fail = 101

class TaskState(Enum):
    scheduled = 1
    running = 2
    success = 3
    skip = 4
    fail = 101


class Config:
    def __init__(self,s):
        y = yaml.load(s)
        self.events = [EventType(e) for e in y.pop('events') ]
        if len(y) > 0:
            raise ValueError("Not supported property: %s" % str(y))
        

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
        self.type = str(v.pop('type'))
        if self.type == 'enum' :
            self.elements = v.pop('elements')
        if len(v) > 0:
            raise ValueError("Not supported property: %s" % str(v))

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

class Event:
    '''
    on event
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
        