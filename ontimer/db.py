"""
This module contains of data access logic.

Examples on this page assumes that you imported ``ontimer.db`` like::

    import ontimer.db as db
    
"""
import hashlib
import datetime
import sqlite3
import os
from . import utils
from . import event
import collections
from enum import IntEnum


default_filename = '.ontimer'

_TBL = 0
_PK  = 1
#                    Table(_TBL)          PKey(_PK)
_EVENTTYPE =         'event_type',        'event_type_id'
_EVENT =             'event',             'event_id'
_TASK =              'task',              'task_id'
_PREREQ =            'task_prereq',       'prereq_id'
_TASKTYPE =          'task_type',         'task_type_id'
_ARTIFACT =          'artifact',          'artifact_id'
_ARTIFACT_SCORE =    'artifact_score',    'artifact_score_id'

class ServerStatus(IntEnum):
    prepare_to_stop  =  -1      
    shutdown = 0    
    running = 1     


server_properties_vars=['server_port','server_host','server_status']

def _conn_decorator(f):
    def decorated(self, *args, **kwargs):
        if kwargs.get('conn'):
            if 'cursor' not in kwargs:
                kwargs['cursor']=kwargs.get('conn').cursor()
            return f(self,*args,**kwargs)
        else:
            conn = self.connect()
            try:
                kwargs['conn']=conn
                kwargs['cursor']=conn.cursor()
                return f(self,*args,**kwargs)
            finally:
                conn.close()
    return decorated

def _fetch_all(cursor, result = None, query=None):
    if query:
        cursor.execute(query)
    if not(result):
        result = cursor.fetchall()
    header=list(cursor.description)
    return list({col[0]:v[i] for (i, col) in enumerate(header)} for v in result)

def _assignments(template, data, whine_if_empty=True ):
    assignments = [ key +' = :_' + key for key in template if '_' + key in data ]
    if whine_if_empty and not(assignments):
        raise ValueError("Have nothing to update: %r", data)
    return ', '.join(assignments)

def _conditions(template, data , whine_if_empty=True):
    conditions = [key + ' = :' + key if data[key] != None else key+' is null' for key in template if key in data ]
    if whine_if_empty and not(conditions):
        raise ValueError("Have nothing to constraint it on: %r", data)
    return ' and '.join(conditions)

def _args(args): return args[0] if 1 == len(args) and isinstance(args[0], collections.Iterable) else args

def _selectors( *args ):
    tables_keys = _args(args)
    return  ', '.join( map( lambda t: t[_TBL] + '.*',tables_keys) )

def _joins ( *args ): 
    tables_keys = _args(args)
    return ' and '.join('%s.%s = %s.%s' % (tables_keys[i + 1][0], tk[1], tk[0], tk[1]) for (i, tk) in enumerate(tables_keys[:-1]))

def _froms ( *args ): 
    tables_keys = _args(args)
    return ', '.join(map(lambda t:t[_TBL], tables_keys))

def _join_froms ( query, l, join,r ): 
    return '%s %s JOIN %s ON %s.%s=%s.%s' % (query,join,r[0],l[0],l[1],r[0],l[1])

def _simple_join(tables_keys, selectors, where = ''):
    return 'select %s from %s where %s %s' % (selectors, _froms(tables_keys), _joins(tables_keys), where)

def _fetch_tree(cursor, key_attrib_pairs, query_result = None, query_columns = None):
    ''' 
    divide query results into sections by key (out of key attrib_pairs) and group by 
    '''
    query_result = query_result or cursor.fetchall()
    if len(query_result) == 0:
        return []
    query_columns = query_columns or [ col[0]  for col in cursor.description ]
    result_with_colnames = map( lambda v: [ (col, v[i]) for i,col in enumerate(query_columns) ], query_result )
    group_list=[]
    for row in result_with_colnames:
        i = 0  
        groups=[{}]  
        for pair in row:
            if i < len(key_attrib_pairs) and key_attrib_pairs[i][0] == pair[0]:
                groups.append({})
                i += 1
            groups[i][pair[0]] = pair[1]
        if len(groups) - 1 != len(key_attrib_pairs):
            raise ValueError('cannot find all keys: %r in query columns: %r , come up with: %r' % (key_attrib_pairs,query_columns,groups) )
        group_list.append(groups)
    def group_by(grp_list, children_keys):
        if len(children_keys)==0 :
            return [ r[0] for r in grp_list]
        regroup = []    
        last_grp_idx = None
        def build_group(start,end):
            keys = children_keys[1:] 
            group = grp_list[start][0]
            regroup.append(group)
            children = group_by([ grp_list[j][1:] for j in range(start, end) ],keys)
            group[children_keys[0]] = children
        for idx, _ in enumerate(grp_list):
            if last_grp_idx is None :
                last_grp_idx = idx
            elif grp_list[idx][0] != grp_list[last_grp_idx][0]:
                build_group(last_grp_idx, idx) 
                last_grp_idx = idx
        build_group(last_grp_idx, len(grp_list)) 
        return regroup
    return group_by(group_list,[pair[1] for pair in key_attrib_pairs])

class Dao:
    def __init__(self, root, filename = default_filename):
        self.root = root
        self.filename = filename
    
    def file(self):
        return os.path.join(self.root,self.filename)   
     
    def exists(self):
        return os.path.exists(self.file())

    def connect(self):
        conn = sqlite3.connect(self.file())
        conn.execute('pragma foreign_keys = on')
        return conn
    
    def ensure_db(self):
        if not(self.exists()) :
            self.create_db()
        else:
            try:
                self.query('select * from settings')
            except:
                self.create_db()

    @_conn_decorator
    def query(self, q, params = None, cursor=None, conn=None):
        r = list(cursor.execute(q,params) if params else cursor.execute(q))
        return r


    def _get_event_tasks_where(self, where, args, cursor, conn):
        query ="select %s from %s where %s and %s %s order by %s" % (
            _selectors(_EVENTTYPE, _EVENT, _TASK, _TASKTYPE),
            _froms(_EVENTTYPE, _EVENT, _TASK, _TASKTYPE),
            _joins(_EVENTTYPE, _EVENT, _TASK), _joins(_TASKTYPE, _TASK), where, 
            'event.scheduled_dt DESC, event.event_id, task.task_id')
        cursor.execute(query,args)
        events = _fetch_tree(cursor,((_TASK[_PK],'tasks'),) )
        tasks = [ t for e in events for t in e['tasks'] ]
        alltasks = { task[_TASK[_PK]] : task for task in tasks }
        dep_q = _simple_join((_EVENT, _TASK, _PREREQ), 
                             'task_prereq.before_task_id, task_prereq.task_id' , 
                             where = where + ' order by 1, 2')
        dependenies = cursor.execute(dep_q,args)
        for d in dependenies:
            utils.safe_append(alltasks[d[1]],'depend_on',d[0])
            utils.safe_append(alltasks[d[0]],'dependents',d[1])
        return events, alltasks

    @_conn_decorator
    def get_event_tasks(self, cutoff = None, cursor = None, conn=None):
        where = 'and (event.updated_dt > :cutoff or event.scheduled_dt > :cutoff) ' 
        args = dict(cutoff = cutoff or  utils.utc_adjusted(hours=-72))
        return self._get_event_tasks_where(where,args,cursor,conn) 

    @_conn_decorator
    def get_event_tasks_by_taskid(self, taskid, cursor=None, conn=None):
        joined = (','.join(str(s) for s in taskid) if hasattr(taskid,'__iter__') else str(taskid) )
        where = 'and event.event_id in (select distinct et.event_id from task et  where et.task_id  in (%s))' % joined  
        return self._get_event_tasks_where(where,{},cursor,conn) 
    
    def get_event_tasks_by_eventid(self, event_id, cursor=None, conn=None):
        joined = (','.join(str(s) for s in event_id) if hasattr(event_id,'__iter__') else str(event_id) )
        where = 'and event.event_id in (%s)' % joined  
        return self._get_event_tasks_where(where,{},cursor,conn) 
    
    @_conn_decorator
    def update_event_tasks_cache(self, cache , cutoff = None, cursor = None, conn=None):
        cutoff = cutoff or  utils.utc_adjusted(days=-31) 
        cache.update(*self.get_event_tasks(cutoff,cursor=cursor,conn=conn))
         
    @_conn_decorator
    def get_tasks_to_run(self, cursor=None, conn=None):
        q = '''select et.* from task et 
            where et.run_at_dt <= ? and et.task_status in (%s) 
            and not exists ( 
            select 'x' from  task_prereq p, task bt 
            where et.task_id = p.task_id 
            and p.before_task_id = bt.task_id and bt.task_status in (%s) )
            ''' % (event.joinEnumsIndices(event.TaskStatus,event.MetaStates.ready),
                   event.joinEnumsIndicesExcept(event.TaskStatus,event.MetaStates.final) )    
        return _fetch_all(cursor, cursor.execute(q,(datetime.datetime.utcnow(),)) )

    @_conn_decorator
    def get_tasks_of_status(self, status, cursor=None, conn=None):
        q = 'select et.* from task et  where et.task_status = ?'    
        return _fetch_all(cursor, cursor.execute(q,(status,)) )

    @_conn_decorator
    def get_events_to_be_completed(self, cursor=None, conn=None):
        q = '''select e.* from event e  
        where e.event_status in (%s) and not exists 
        (select 'x' from task et 
        where e.event_id = et.event_id and et.task_status in (%s) )
        ''' % (event.joinEnumsIndices(event.EventStatus,event.MetaStates.active),
              event.joinEnumsIndicesExcept(event.TaskStatus,event.MetaStates.final) )     
        return _fetch_all(cursor, cursor.execute(q) )

    @_conn_decorator
    def update_event(self, event_data, cursor=None, conn=None):
        if utils.find_enum(event.EventStatus,event_data['_event_status']).isMetaStatus(event.MetaStates.final) :
            event_data.update(_finished_dt = datetime.datetime.utcnow())
        set_vars = _assignments([
            'event_status',
            'finished_dt',
            'eta_dt',
            ],event_data)
        
        newstate = dict(event_data)
        newstate.update(utc_now = datetime.datetime.utcnow( ))
        cursor.execute(''' update event set 
             updated_dt = :utc_now,
             %s 
             where
             event_id = :event_id and
             event_status = :event_status
            ''' % set_vars , newstate)
        if cursor.rowcount == 1 :
            conn.commit()
            return True
        return False
    
    @_conn_decorator
    def load_active_generators(self, cursor=None, conn=None):
        cursor.execute(''' 
        SELECT generator.*, event_type.event_name, event.* 
        FROM event_type JOIN generator ON event_type.event_type_id=generator.event_type_id 
        LEFT OUTER JOIN event ON generator.current_event_id=event.event_id
        where generator.last_seen_in_config_id = (select current_config_id from settings where settings_id = 1)
        ''' )
        generators = _fetch_tree(cursor, ( ('event_id','current_event'), ) )
        for g in generators:
            g['current_event'] = g['current_event'][0]
            if not(g['current_event']['event_id']) :
                g['current_event'] = None
        return generators
     

        
    @_conn_decorator
    def update_task(self, task, cursor=None, conn=None):
        set_vars = _assignments([
              'task_status',
              'run_count',
              'task_state',
              'last_run_outcome',
              'run_at_dt',
              ],task)
        newtask = dict(task)
        newtask.update(utc_now = datetime.datetime.utcnow( ))
        cursor.execute('''update task set 
             updated_dt = :utc_now,
             %s
             where
             task_id = :task_id and
             updated_dt = :updated_dt and
             task_status = :task_status
            ''' % set_vars, newtask)
        if cursor.rowcount == 1 :
            cursor.execute('''update event 
                set  updated_dt = :utc_now 
                where event_id = :event_id
                ''', newtask)
            if cursor.rowcount == 1 :
                conn.commit()
                return True
        return False

    @_conn_decorator
    def load_task(self, task, cursor=None, conn=None):
        result = list(cursor.execute('''select et.* from task et 
        where et.task_id = :task_id''', task))
        if len(result)!=1:
            raise AssertionError('expect to get one instead of %d record for %r ' % (len(result),task) )
        return _fetch_all( cursor, result )[0]
        
    @_conn_decorator
    def store_artifact(self, artifact, cursor=None, conn=None):
        artifact = dict(artifact)
        artifact.update(utc_now = datetime.datetime.utcnow( ))
        cursor.execute('''UPDATE artifact SET value = :value, stored_dt = :utc_now 
            WHERE  task_id = :task_id and run = :run and name = :name
            ''', artifact)
        if cursor.rowcount == 0 :
            cursor.execute('''INSERT INTO artifact (task_id, run, name, value, stored_dt) 
                VALUES ( :task_id, :run,  :name, :value, :utc_now)
                ''', artifact)
        elif cursor.rowcount != 1:
            raise AssertionError('unexpected row count: %d storing: %r' % (cursor.rowcount, artifact))
        conn.commit()

    @_conn_decorator
    def add_artifact_score(self, score, cursor=None, conn=None):
        result = list(cursor.execute('''SELECT artifact_id FROM artifact
            WHERE  task_id = :task_id and run = :run and name = :name
            ''', score))
        score = dict(score)
        score.update(utc_now = datetime.datetime.utcnow( ))
        if len(result) == 0 :
            cursor.execute('''INSERT INTO artifact (task_id, run, name, value, stored_dt) 
                VALUES ( :task_id, :run, :name, NULL, :utc_now)
                ''', score)
            score.update(artifact_id = cursor.lastrowid)
        elif len(result) == 1 :
            score.update(artifact_id = result[0][0])
        else:
            raise AssertionError('too many artifact_ids: %r for %r' % score)
        cursor.execute('''INSERT INTO artifact_score (artifact_id, score, updated_dt) 
            VALUES (:artifact_id, :score, :utc_now );
            ''', score)
        conn.commit()

    @_conn_decorator
    def get_artifacts_for_run(self, taskid, run, cursor=None, conn=None):
        query ="""select %s from %s where task.task_id = :task_id and artifact.run = :run 
        order by artifact.artifact_id, artifact.stored_dt, artifact_score.updated_dt""" % (
            _selectors(_TASK, _ARTIFACT, _ARTIFACT_SCORE),
            _join_froms( _join_froms( _TASK[_TBL], _TASK, '', _ARTIFACT), _ARTIFACT, 'OUTER LEFT', _ARTIFACT_SCORE) )
        cursor.execute(query,{'task_id':taskid,'run':run})
        task = _fetch_tree(cursor, ((_ARTIFACT[_PK], 'artifacts'), (_ARTIFACT_SCORE[_PK], 'scores')))[0]
        artifacts_list = task['artifacts']
        for r in artifacts_list:
            if len(r['scores'])==1 and all(v is None for v in r['scores'][0].itervalues()) :
                del r['scores']
        task['artifacts']={ r['name'] : r for r in artifacts_list}
        return  task
        
    @_conn_decorator
    def emit_event(self, event, cursor=None, conn=None):
        conn.commit()
        cursor.execute('''insert into event 
            (event_type_id,event_string,event_status,generator_id,scheduled_dt,eta_dt) 
            values (?, ?, ?, ?, ?, ?)''', 
            (event.type.event_type_id,str(event),event.status.value,event.generator_id(),event.scheduled_dt,event.eta_dt))
        event.event_id = cursor.lastrowid
        if event.generator:
            if event.generator['current_event_id'] :
                event.generator['_prev_event_id']=event.generator['current_event_id'] 
            event.generator['_current_event_id']=event.event_id 
            varialbles = [ 'ontime_state', 'prev_event_id', 'current_event_id' ]
            set_vars = _assignments(varialbles,event.generator)
            conds = _conditions(varialbles,event.generator)
            q = ''' update generator set %s 
                 where generator_id = :generator_id and %s
                ''' % (set_vars,conds)
            cursor.execute(q , event.generator )
            if cursor.rowcount != 1 :
                conn.rollback()
                raise ValueError('cannot update generator')
        task_dict = {}
        for t in event.tasks() :
            task_dict[t.task_name()]=t
            cursor.execute('''insert into task 
                (event_id, task_type_id, task_state, task_status, run_at_dt, updated_dt) 
                values (?, ?, ?, ?, ?, ?)''', 
                (event.event_id,t.task_type_id(),t.state(),t.status.value,t.run_at_dt,datetime.datetime.utcnow()))
            t.task_id =  cursor.lastrowid
        for t in event.tasks() :
            if t.task.depends_on :
                for upstream in t.task.depends_on :
                    cursor.execute('''insert into task_prereq 
                                (before_task_id, task_id) 
                                values (?, ?)''', 
                                (task_dict[upstream].task_id, t.task_id))
        conn.commit()
        return event
        
    @_conn_decorator
    def set_config(self,config_text,cursor=None,conn=None):
        event.Config(config_text)
        r = self.get_config(cursor=cursor, conn=conn)
        sha1 = hashlib.sha1(config_text).hexdigest()
        if not(r) or r[3] != sha1:
            cursor.execute("insert into config (uploaded_dt,config_text,config_sha1) values (CURRENT_TIMESTAMP,?,?)",(config_text,sha1))
            cursor.execute("update settings set current_config_id = ?, last_changed_dt=CURRENT_TIMESTAMP",(cursor.lastrowid,))
            conn.commit()
            return True
        return False

    @_conn_decorator
    def reset_running_tasks(self,cursor=None,conn=None):
        '''
        reset all ``running`` tasks to ``fail`` to ensure there no tasks left behind after 
        crash/forced stop of ontimer
        '''
        cursor.execute("update task set task_status = %d where task_status = %d" 
                       % (event.TaskStatus.fail, event.TaskStatus.running) )
        conn.commit()
        return cursor.rowcount

    @_conn_decorator
    def apply_config(self,cursor=None,conn=None):
        r = self.get_config(conn=conn)
        config = event.Config(r[2])
        config.config_id = r[0]
        for event_type in config.events:
            r = list(cursor.execute("select event_type_id, last_seen_in_config_id from event_type where event_name = ?",(event_type.name,)))
            if len(r) > 1 :
                raise ValueError('duplicate for event_name: %s' % event_type.name)
            elif len(r) == 1:
                event_type.event_type_id = r[0][0]
                if r[0][1] != config.config_id:
                    cursor.execute("update event_type set last_seen_in_config_id = ? where  event_type_id = ?",(config.config_id,event_type.event_type_id))
            else:
                cursor.execute("insert into event_type (event_name,last_seen_in_config_id) values (?,?)",(event_type.name,config.config_id))
                event_type.event_type_id = cursor.lastrowid
            
            def update_ids(obj_list,name, namecol):
                for obj in obj_list:
                    obj_id = None
                    r = list(cursor.execute("select {0}_id, last_seen_in_config_id from {0} where {1} = ? and event_type_id = ?".format(name,namecol),
                                            (obj.name,event_type.event_type_id)))
                    if len(r) > 1 :
                        raise ValueError('duplicate %s: %s' % name, obj.name)
                    elif len(r) == 1:
                        obj_id = r[0][0]
                        if r[0][1] != config.config_id:
                            cursor.execute("update {0} set last_seen_in_config_id = ? where  {0}_id = ?".format(name,namecol),(config.config_id,obj_id))
                    else:
                        cursor.execute("insert into {0} ({1},event_type_id,last_seen_in_config_id) values (?,?,?)".format(name,namecol),
                                       (obj.name,event_type.event_type_id,config.config_id))
                        obj_id = cursor.lastrowid
                    setattr(obj,'%s_id' % name, obj_id)
                    
            update_ids(event_type.generators,'generator', 'generator_name')
            update_ids(event_type.tasks,'task_type', 'task_name')
            
        conn.commit()
        return config
            
    @_conn_decorator
    def set_global_var(self,key,value,cursor=None,conn=None):
        cursor.execute('UPDATE global_variables SET value = ? WHERE key = ?',(value,key))    
        if 0 == cursor.rowcount:
            cursor.execute('INSERT INTO global_variables (value,key) VALUES (?,?)',(value,key))
        elif 1 != cursor.rowcount:
            raise ValueError('wierd rowcount:%d',cursor.rowcount)
        conn.commit()

    @_conn_decorator
    def get_global_vars(self,cursor=None,conn=None):
        return dict(cursor.execute('SELECT key, value FROM global_variables'))   
        
    @_conn_decorator
    def get_config(self,config_id=None,cursor=None, conn=None):
        if not(config_id):
            config_id = list(cursor.execute('select current_config_id from settings'))[0][0]
            if not(config_id):
                return None
        return list(cursor.execute('select config_id,uploaded_dt,config_text,config_sha1 from config where config_id = ?', (config_id,)))[0]

    @_conn_decorator
    def get_server_properties(self,cursor=None, conn=None):
        q = 'select %s from settings where settings_id = 1' % ','.join(server_properties_vars)
        return dict(zip( server_properties_vars, next(cursor.execute( q ))))

    @_conn_decorator
    def set_server_properties(self,server_props, cursor=None, conn=None):
        set_vars = _assignments(server_properties_vars,server_props)
        cursor.execute('''update settings set %s 
             where settings_id = 1 and
             server_status = :server_status
            ''' % set_vars , server_props)
        if cursor.rowcount == 1 :
            conn.commit()
            return True
        return False        

    @_conn_decorator
    def create_db(self, cursor=None, conn=None):
        cursor.execute('''CREATE TABLE event_type (
        event_type_id INTEGER primary key,
        event_name TEXT, 
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        cursor.execute('''CREATE TABLE event (
        event_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        event_string TEXT, 
        event_status INTEGER CHECK( event_status IN (%s) ) NOT NULL,
        generator_id INTEGER references generator(generator_id),
        scheduled_dt TIMESTAMP not null,
        finished_dt TIMESTAMP ,
        eta_dt TIMESTAMP, 
        updated_dt TIMESTAMP 
        )''' % event.joinEnumsIndices(event.EventStatus,event.MetaStates.all) )
    
        cursor.execute('''CREATE TABLE task_type (
        task_type_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        task_name TEXT,
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        cursor.execute('''CREATE TABLE task (
        task_id INTEGER primary key,
        event_id INTEGER references event(event_id),
        task_type_id INTEGER references task_type(task_type_id),
        task_state TEXT,
        task_status INTEGER CHECK( task_status IN (%s) ) NOT NULL DEFAULT 1,
        run_count INTEGER DEFAULT 0,
        last_run_outcome INTEGER CHECK( last_run_outcome IN (%s) ) NULL DEFAULT NULL,
        updated_dt TIMESTAMP not null,
        run_at_dt TIMESTAMP not null
        )'''% ( event.joinEnumsIndices(event.TaskStatus,event.MetaStates.all),  
                event.joinEnumsIndices(event.RunOutcome,event.MetaStates.all) ) )
   
        cursor.execute('''CREATE TABLE task_prereq (
        prereq_id INTEGER primary key,
        before_task_id INTEGER references task(task_id ),
        task_id INTEGER references task(task_id )
        )''' )
        
        cursor.execute('''CREATE TABLE artifact (
        artifact_id INTEGER primary key,
        task_id INTEGER references task(task_id),
        run INTEGER not null,
        name TEXT,
        value TEXT null,
        stored_dt TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE artifact_score (
        artifact_score_id INTEGER primary key,
        artifact_id INTEGER references artifact(artifact_id),
        score INTEGER,
        updated_dt TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE generator (
        generator_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        generator_name TEXT, 
        ontime_state TIMESTAMP null,
        prev_event_id INTEGER null references event(event_id) ,
        current_event_id INTEGER null references event(event_id),
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        cursor.execute('''CREATE TABLE config (
        config_id INTEGER primary key,
        uploaded_dt TIMESTAMP,
        config_text TEXT,
        config_sha1 TEXT
        )''')
    
        cursor.execute('''CREATE TABLE global_variables (
        global_var_id INTEGER primary key,
        key TEXT unique not null,
        value TEXT 
        )''')

        cursor.execute('''CREATE TABLE settings (
        settings_id INTEGER primary key CHECK( settings_id in (1) ) default 1,
        current_config_id INTEGER null references config(config_id) default null,
        server_port INTEGER null default null,
        server_host TEXT null default null,
        server_status INTEGER not null default 0,
        last_changed_dt TIMESTAMP default CURRENT_TIMESTAMP
        )''')
        
        # Save (commit) the changes
        cursor.execute('insert into settings (settings_id) values (1)')
        #
        conn.commit()
    
        
    
