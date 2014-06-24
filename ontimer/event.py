'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import Enum

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

class EventType:
    '''
    on event
    '''


    def __init__(self,yaml):
        '''
        Constructor
        '''
        pass

class Event:
    '''
    on event
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
        