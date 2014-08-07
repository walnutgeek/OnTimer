'''
Created on Jul 11, 2014

@author: sergeyk
'''
import datetime

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
    for f in formats:
        try:
            return datetime.datetime.strptime(s, f)
        except:
            pass
    raise ValueError('Cannot parse "%s", tried %s',s,str(formats))


def quict(**kwargs): 
    ''' quick way to create dict() '''
    return kwargs


