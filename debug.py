from __future__ import print_function
from ontimer.dpt import *

from ontimer import event , utils, db
from datetime import datetime
dao=db.Dao('./root')
config=dao.apply_config()

'''
gens = [event.Generator(config,gen_data) for gen_data in dao.load_active_generators()]
             
$python -i debug.py
import datetime
dt=datetime.datetime(2014,9,15)
dao.set_global_var('ipy_path','/Users/sergeyk/ipyhome/')
dao.emit_event(gens[1].setupEvent(dt))

$python -m ontimer.app --root root/ --config sample-config.yaml server
''' 


# from ontimer.tests.test_db import *
# import time
# import ontimer.event
# from ontimer import utils
# test_dbcreation()
# test_set_global_var()
# test_emit()
# events,tasks=dao.get_event_tasks()
# print utils.utc_adjusted(hours=-6)
          
            