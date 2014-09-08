from ontimer import event , utils, db
from datetime import datetime
dao=db.Dao('./root')
config=dao.apply_config()
gens = [event.Generator(config,gen_data) for gen_data in dao.load_active_generators()]
             


# from ontimer.tests.test_db import *
# import time
# import ontimer.event
# from ontimer import utils
# test_dbcreation()
# test_set_global_var()
# test_emit()
# events,tasks=dao.get_event_tasks()
# print utils.utc_adjusted(hours=-6)
          
            