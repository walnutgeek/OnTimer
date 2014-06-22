'''
Created on Jun 21, 2014

@author: sergeyk
'''
from enum import Enum

EventState = Enum('EventState','active eta_breach success skip fail')
TaskState = Enum('TaskState','scheduled running success skip not_applicable fail')

class Event:
    '''
    on event
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
        