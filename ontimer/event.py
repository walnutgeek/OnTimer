'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import Enum
import yaml

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
        eventTypeList = y.pop('events') 
        self.events = [EventType(e) for e in eventTypeList]
        if len(y) > 0:
            raise ValueError("Not supported property: %s" % str(y))
        

class EventType:
    def __init__(self,y):
        self.name = str(y.pop('name'))
        varsList = y.pop('vars') 
        self.vars = [VarDef(v) for v in varsList ]
        generatorsList = y.pop('generators',None) #optional
        self.generators = [ GenDef(g) for g in generatorsList] if generatorsList else []
        tasksList = y.pop('tasks') 
        self.tasks = [ TaskDef(t) for t in tasksList]
        if len(y) > 0:
            raise ValueError("Not supported property: %s" % str(y))


class VarDef:
    def __init__(self, v):
        pass

class GenDef:
    def __init__(self, v):
        pass
    
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
        