from ontimer.tests.test_db import *
import time
import ontimer.event
from ontimer import utils
test_dbcreation()
test_set_global_var()
test_emit()
events,tasks=dao.get_event_tasks()
print utils.utc_adjusted(hours=-6)
          
            