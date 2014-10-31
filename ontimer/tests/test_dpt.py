from nose.tools import eq_, with_setup
from .. import dpt
from .. import utils


def failing(e,t):
    b = False
    try:
        t()
    except e:
        b = True
    return b

def test_Elem():
    s31 = dpt.PathElem("s31")
    eq_(s31.s, 's')
    eq_(s31.n, 31)
    another_s31 = dpt.PathElem("s",31)
    eq_(s31, another_s31)
    eq_(True,failing(ValueError,lambda: dpt.PathElem('a')))
    eq_(True,failing(ValueError,lambda: dpt.PathElem('as','z')))
    eq_(True,failing(ValueError,lambda: dpt.PathElem('as',5)))
    
def test_Path():
    s31 = dpt.Path("s31")
    eq_(s31.elems[0].s, 's')
    eq_(s31.elems[0].n, 31)
    another_s31 = dpt.Path("s31")
    eq_(s31, another_s31)
    path = dpt.Path("z31g15")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    eq_(path.elems[1].s, 'g')
    eq_(path.elems[1].n, 15)
    path = dpt.Path("l18r3")
    eq_(path.elems[0].s, 'l')
    eq_(path.elems[0].n, 18)
    eq_(path.elems[1].s, 'r')
    eq_(path.elems[1].n, 3)

    path = dpt.Path("e3")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    eq_(path.elems[1].s, 'e')
    eq_(path.elems[1].n, 3)

    path = dpt.Path("")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    
    eq_(True,failing(ValueError,lambda: dpt.Path(4)))
    eq_(True,failing(ValueError,lambda: dpt.Path('4')))
    eq_(True,failing(ValueError,lambda: dpt.Path("r3")))
    eq_(True,failing(ValueError,lambda: dpt.Path("e17E3")))
    eq_(True,failing(ValueError,lambda: dpt.Path("q3")))

    p1 = dpt.Path("z31")
    p2 = dpt.Path("e3")
    eq_(True,p2.isdecendant(p1))
    eq_(False,p1.isdecendant(p2))
    
    eq_(repr(p1),"'z31'")
 
def test_filter():
    as_of = utils.toDateTime('2014-10-30 23:59:00')
    events = [
         {'scheduled_dt': u'2014-10-30 17:00:00', 'updated_dt': None, 
          'tasks': [
                    {'updated_dt': u'2014-10-30 05:00:01.899047', 'task_status': 1, 'task_type_id': 3, 'task_id': 199, 'event_id': 34, 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'start', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss --bs 9"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}, 
                    {'updated_dt': u'2014-10-30 05:00:01.899186', 'task_status': 1, 'task_type_id': 4, 'task_id': 200, 'event_id': 34, 'depend_on': [199], 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'branch1', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss --bs 23"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}, 
                    {'updated_dt': u'2014-10-30 05:00:01.899259', 'task_status': 1, 'task_type_id': 5, 'task_id': 201, 'event_id': 34, 'depend_on': [199], 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'branch2', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss --bs 12"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}, 
                    {'updated_dt': u'2014-10-30 05:00:01.899327', 'task_status': 1, 'task_type_id': 6, 'task_id': 202, 'event_id': 34, 'depend_on': [200, 201], 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'join1', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}, 
                    {'updated_dt': u'2014-10-30 05:00:01.899394', 'task_status': 1, 'task_type_id': 7, 'task_id': 203, 'event_id': 34, 'depend_on': [202, 204], 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'join2', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss --bs 7"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}, 
                    {'updated_dt': u'2014-10-30 05:00:01.899460', 'task_status': 1, 'task_type_id': 8, 'task_id': 204, 'event_id': 34, 'depend_on': [201], 'run_at_dt': u'2014-10-30 17:00:00', 'task_name': u'branch3', 'event_type_id': 2, 'run_count': 0, 'task_state': u'{"cmd": "boss --bs 36"}', 'last_seen_in_config_id': 1, 'last_run_outcome': None}], 
          'event_string': u'tree,2014-10-30 10:00:00', 'event_name': u'tree', 'eta_dt': None, 'event_id': 34, 'event_type_id': 2, 'generator_id': 2, 'event_status': 1, 'finished_dt': None, 'last_seen_in_config_id': 1}, 
         {'scheduled_dt': u'2014-10-29 17:00:00', 'updated_dt': u'2014-10-29 23:55:51.897593', 
          'tasks': [
                    {'updated_dt': u'2014-10-29 23:53:26.834453', 'task_status': 101, 'task_type_id': 3, 'task_id': 193, 'event_id': 33, 'run_at_dt': u'2014-10-29 23:53:11.896597', 'task_name': u'start', 'event_type_id': 2, 'run_count': 2, 'task_state': u'{"cmd": "boss --bs 9"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-29 23:54:00.154836', 'task_status': 101, 'task_type_id': 4, 'task_id': 194, 'event_id': 33, 'depend_on': [193], 'run_at_dt': u'2014-10-29 17:00:00', 'task_name': u'branch1', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 23"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-29 23:54:01.136554', 'task_status': 101, 'task_type_id': 5, 'task_id': 195, 'event_id': 33, 'depend_on': [193], 'run_at_dt': u'2014-10-29 23:53:46.896707', 'task_name': u'branch2', 'event_type_id': 2, 'run_count': 2, 'task_state': u'{"cmd": "boss --bs 12"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-29 23:54:05.758180', 'task_status': 101, 'task_type_id': 6, 'task_id': 196, 'event_id': 33, 'depend_on': [194, 195], 'run_at_dt': u'2014-10-29 17:00:00', 'task_name': u'join1', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-29 23:55:47.111369', 'task_status': 101, 'task_type_id': 7, 'task_id': 197, 'event_id': 33, 'depend_on': [196, 198], 'run_at_dt': u'2014-10-29 17:00:00', 'task_name': u'join2', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 7"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-29 23:55:32.339529', 'task_status': 101, 'task_type_id': 8, 'task_id': 198, 'event_id': 33, 'depend_on': [195], 'run_at_dt': u'2014-10-29 23:54:51.896363', 'task_name': u'branch3', 'event_type_id': 2, 'run_count': 2, 'task_state': u'{"cmd": "boss --bs 36"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}], 
          'event_string': u'tree,2014-10-29 10:00:00', 'event_name': u'tree', 'eta_dt': None, 'event_id': 33, 'event_type_id': 2, 'generator_id': 2, 'event_status': 101, 'finished_dt': u'2014-10-29 23:55:51.897582', 'last_seen_in_config_id': 1}, 
         {'scheduled_dt': u'2014-10-28 17:00:00', 'updated_dt': u'2014-10-28 22:11:06.897774', 
          'tasks': [
                    {'updated_dt': u'2014-10-28 22:09:16.832567', 'task_status': 101, 'task_type_id': 3, 'task_id': 187, 'event_id': 32, 'run_at_dt': u'2014-10-28 17:00:00', 'task_name': u'start', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 9"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 22:09:39.484009', 'task_status': 101, 'task_type_id': 4, 'task_id': 188, 'event_id': 32, 'depend_on': [187], 'run_at_dt': u'2014-10-28 17:00:00', 'task_name': u'branch1', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 23"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 22:09:30.946005', 'task_status': 101, 'task_type_id': 5, 'task_id': 189, 'event_id': 32, 'depend_on': [187], 'run_at_dt': u'2014-10-28 17:00:00', 'task_name': u'branch2', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 12"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 22:09:45.954320', 'task_status': 101, 'task_type_id': 6, 'task_id': 190, 'event_id': 32, 'depend_on': [188, 189], 'run_at_dt': u'2014-10-28 17:00:00', 'task_name': u'join1', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 22:11:04.052081', 'task_status': 101, 'task_type_id': 7, 'task_id': 191, 'event_id': 32, 'depend_on': [190, 192], 'run_at_dt': u'2014-10-28 22:10:51.895741', 'task_name': u'join2', 'event_type_id': 2, 'run_count': 3, 'task_state': u'{"cmd": "boss --bs 7"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 22:10:11.892805', 'task_status': 101, 'task_type_id': 8, 'task_id': 192, 'event_id': 32, 'depend_on': [189], 'run_at_dt': u'2014-10-28 17:00:00', 'task_name': u'branch3', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 36"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}], 
          'event_string': u'tree,2014-10-28 10:00:00', 'event_name': u'tree', 'eta_dt': None, 'event_id': 32, 'event_type_id': 2, 'generator_id': 2, 'event_status': 101, 'finished_dt': u'2014-10-28 22:11:06.897764', 'last_seen_in_config_id': 1},
         {'scheduled_dt': u'2014-10-27 17:00:00', 'updated_dt': u'2014-10-28 02:36:26.897257', 
          'tasks': [
                    {'updated_dt': u'2014-10-28 02:34:57.107150', 'task_status': 101, 'task_type_id': 3, 'task_id': 181, 'event_id': 31, 'run_at_dt': u'2014-10-27 17:00:00', 'task_name': u'start', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 9"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 02:35:29.252625', 'task_status': 101, 'task_type_id': 4, 'task_id': 182, 'event_id': 31, 'depend_on': [181], 'run_at_dt': u'2014-10-27 17:00:00', 'task_name': u'branch1', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 23"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101},
                    {'updated_dt': u'2014-10-28 02:35:12.655690', 'task_status': 101, 'task_type_id': 5, 'task_id': 183, 'event_id': 31, 'depend_on': [181], 'run_at_dt': u'2014-10-27 17:00:00', 'task_name': u'branch2', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 12"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 02:35:55.890074', 'task_status': 101, 'task_type_id': 6, 'task_id': 184, 'event_id': 31, 'depend_on': [182, 183], 'run_at_dt': u'2014-10-28 02:35:46.897172', 'task_name': u'join1', 'event_type_id': 2, 'run_count': 2, 'task_state': u'{"cmd": "boss"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 02:36:22.597447', 'task_status': 101, 'task_type_id': 7, 'task_id': 185, 'event_id': 31, 'depend_on': [184, 186], 'run_at_dt': u'2014-10-28 02:36:11.896739', 'task_name': u'join2', 'event_type_id': 2, 'run_count': 2, 'task_state': u'{"cmd": "boss --bs 7"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}, 
                    {'updated_dt': u'2014-10-28 02:35:54.882852', 'task_status': 101, 'task_type_id': 8, 'task_id': 186, 'event_id': 31, 'depend_on': [183], 'run_at_dt': u'2014-10-27 17:00:00', 'task_name': u'branch3', 'event_type_id': 2, 'run_count': 1, 'task_state': u'{"cmd": "boss --bs 36"}', 'last_seen_in_config_id': 1, 'last_run_outcome': 101}], 
          'event_string': u'tree,2014-10-27 10:00:00', 'event_name': u'tree', 'eta_dt': None, 'event_id': 31, 'event_type_id': 2, 'generator_id': 2, 'event_status': 101, 'finished_dt': u'2014-10-28 02:36:26.897245', 'last_seen_in_config_id': 1}]
    
    z1 = dpt.Path('z1')
    z1_data = z1.filter(events, as_of)
    eq_(len(z1_data),1)
    eq_(len(z1_data[0]['tasks']),6)
    
    z1T5 = dpt.Path('z1T5')
    z1T5_data = z1T5.filter(events, as_of)
    eq_(len(z1T5_data),1)
    eq_(len(z1T5_data[0]['tasks']),1)
    z1T15 = dpt.Path('z1T15')
    z1T15_data = z1T15.filter(events, as_of)
    eq_(len(z1T15_data),0)
    z1g2 = dpt.Path('z1g2').filter(events, as_of)
    eq_(len(z1g2),1)
    eq_(len(z1g2[0]['tasks']),6)
    failing(ValueError,lambda: dpt.Path('l15r3').filter(events, as_of))
    failing(ValueError,lambda: dpt.Path('l15r3').isdecendant(z1T15))
    failing(ValueError,lambda: z1T15.isdecendant(dpt.Path('l15r3')))
    
