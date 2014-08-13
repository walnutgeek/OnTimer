import hashlib
import datetime
import sqlite3
import os
from . import event
import collections

default_filename = '.ontimer'

_TBL = 0
_PK  = 1
#          Table(_TBL)          PKey(_PK)
_TYPE =    'event_type',        'event_type_id'
_EVENT =   'event',             'event_id'
_TASK =    'event_task',        'event_task_id'
_PREREQ =  'event_task_prereq', 'prereq_id'
_TASKDEF = 'task',              'task_id'

def _conn_decorator(f):
    def magic(self, *args, **kwargs):
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
    return magic

def _fetchAllRecords(cursor, result):
    return list({col[0]:v[i] for (i, col) in enumerate(cursor.description)} for v in result)

def _assignments(template, data ):
    assignments = []
    for key in template:
        dirty_key = '_' + key 
        if dirty_key in data:
            assignments.append('%s = :%s' % (key,dirty_key) )
    if not(assignments):
        raise ValueError("Have nothing to update: %r", data)
    return ', '.join(assignments)

def _conditions(template, data ):
    conditions = ['%s = :%s' % (key,key) for key in template if key in data]
    if not(conditions):
        raise ValueError("Have nothing to update: %r", data)
    return ', '.join(conditions)

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

def _generate_join(tables_keys, selectors, where = ''):
    return 'select %s from %s where %s %s' % (selectors, _froms(tables_keys), _joins(tables_keys), where)

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
    def query(self, q, params=None, cursor=None, conn=None):
        r = list(cursor.execute(q,params) if params else cursor.execute(q))
        return r

    @_conn_decorator
    def tree_query(self, tables_keys, accdict_names, where='', customize = None, cursor=None, conn=None):
        query_result = list(cursor.execute(_generate_join(tables_keys, _selectors(tables_keys), where)) )
        result_with_colnames = map( lambda v: [ (col[0], v[i]) for i,col in enumerate(cursor.description) ], query_result )
        topdict={}
        for r in result_with_colnames:
            i = -1  
            groups=[]  
            for v in r:
                if i+1 < len(tables_keys) and tables_keys[i+1][_PK] == v[0]:
                    groups.append({})
                    i += 1
                if i >= 0 :
                    groups[i][v[0]] = v[1]
            curdict=topdict
            for i in range(len(groups)):
                g_key_val=groups[i][tables_keys[i][_PK]]
                if g_key_val in curdict:
                    if i < len(accdict_names):
                        groups[i] = curdict[g_key_val]
                        curdict=groups[i][accdict_names[i]]
                else:
                    curdict[g_key_val]=groups[i]
                    if i < len(accdict_names):
                        curdict={}
                        groups[i][accdict_names[i]]=curdict
            if customize:
                customize(groups,topdict)
        return topdict

    
    @_conn_decorator
    def get_active_events(self, cursor = None, conn=None):
        where = 'and event.event_status in (%s)' % event.joinEnumsIndices(event.EventStatus,event.MetaStates.active)
        alltasks={}
        allevents={}
        def populate_alltasks(groups,topdict):
            allevents[groups[1][_EVENT[_PK]]]=groups[1]
            alltasks[groups[2][_TASK[_PK]]]=groups[2]
        alltypes = self.tree_query((_TYPE, _EVENT, _TASK), ('events', 'tasks'), where, customize=populate_alltasks, cursor=cursor, conn=conn)
        dependenies = cursor.execute(_generate_join((_TYPE, _EVENT, _TASK, _PREREQ), 'event_task_prereq.before_task_id, event_task_prereq.event_task_id' , where = where ))
        for d in dependenies:
            task=alltasks[d[1]]
            if 'depend_on' in task:
                task['depend_on'].append(d[0])
            else:
                task['depend_on'] = [d[0]]
        return alltypes, allevents, alltasks

         
    @_conn_decorator
    def get_tasks_to_run(self, cursor=None, conn=None):
        q = '''select et.* from event_task et 
            where et.run_at_dt <= ? and et.task_status in (%s) 
            and not exists ( 
            select 'x' from  event_task_prereq p, event_task bt 
            where et.event_task_id = p.event_task_id 
            and p.before_task_id = bt.event_task_id and bt.task_status in (%s) )
            ''' % (event.joinEnumsIndices(event.TaskStatus,event.MetaStates.ready),
                   event.joinEnumsIndicesExcept(event.TaskStatus,event.MetaStates.final) )    
        return _fetchAllRecords(cursor, cursor.execute(q,(datetime.datetime.utcnow(),)) )

    @_conn_decorator
    def get_tasks_of_status(self, status, cursor=None, conn=None):
        q = 'select et.* from event_task et  where et.task_status = ?'    
        return _fetchAllRecords(cursor, cursor.execute(q,(status,)) )

    @_conn_decorator
    def get_events_to_be_completed(self, cursor=None, conn=None):
        q = '''select e.* from event e  
        where e.event_status in (%s) and not exists 
        (select 'x' from event_task et 
        where e.event_id = et.event_id and et.task_status in (%s) )
        ''' % (event.joinEnumsIndices(event.EventStatus,event.MetaStates.active),
              event.joinEnumsIndicesExcept(event.TaskStatus,event.MetaStates.final) )     
        return _fetchAllRecords(cursor, cursor.execute(q) )

    @_conn_decorator
    def update_event(self, event, cursor=None, conn=None):
        set_vars = _assignments([
              'event_status',
              'finished_dt',
              'eta_dt',
              ],event)
        newstate = dict(event)
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
        cursor.execute('''update event_task set 
             updated_dt = :utc_now,
             %s
             where
             event_task_id = :event_task_id and
             updated_dt = :updated_dt and
             task_status = :task_status
            ''' % set_vars, newtask)
        if cursor.rowcount == 1 :
            conn.commit()
            return True
        return False

    @_conn_decorator
    def load_task(self, task, cursor=None, conn=None):
        result = list(cursor.execute('''select et.* from event_task et 
        where et.event_task_id = :event_task_id''', task))
        if len(result)!=1:
            raise ValueError('expect to get one instead of %d record for %r ' % (len(result),task) )
        return _fetchAllRecords( cursor, result )[0]
        
    @_conn_decorator
    def store_artifact(self, artifact, cursor=None, conn=None):
        artifact = dict(artifact)
        artifact.update(utc_now = datetime.datetime.utcnow( ))
        cursor.execute('''UPDATE artifact SET value = :value, stored_dt = :utc_now 
            WHERE  event_task_id = :event_task_id and run = :run and name = :name
            ''', artifact)
        if cursor.rowcount == 0 :
            cursor.execute('''INSERT INTO artifact (event_task_id, run, name, value, stored_dt) 
                VALUES ( :event_task_id, :run,  :name, :value, :utc_now)
                ''', artifact)
        elif cursor.rowcount != 1:
            raise ValueError('unexpected row count: %d storing: %r' % (cursor.rowcount, artifact))
        conn.commit()

    @_conn_decorator
    def add_artifact_score(self, score, cursor=None, conn=None):
        result = list(cursor.execute('''SELECT artifact_id FROM artifact
            WHERE  event_task_id = :event_task_id and run = :run and name = :name
            ''', score))
        score = dict(score)
        score.update(utc_now = datetime.datetime.utcnow( ))
        if len(result) == 0 :
            cursor.execute('''INSERT INTO artifact (event_task_id, run, name, value, stored_dt) 
                VALUES ( :event_task_id, :run, :name, NULL, :utc_now)
                ''', score)
            score.update(artifact_id = cursor.lastrowid)
        elif len(result) == 1 :
            score.update(artifact_id = result[0][0])
        else:
            raise ValueError('too many artifact_ids: %r for %r' % score)
        cursor.execute('''INSERT INTO artifact_score (artifact_id, score, updated_dt) 
            VALUES (:artifact_id, :score, :utc_now );
            ''', score)
        conn.commit()
        
    @_conn_decorator
    def emit_event(self, event, cursor=None, conn=None):
        cursor.execute('''insert into event 
            (event_type_id,event_string,event_status,generator_id,started_dt,eta_dt) 
            values (?, ?, ?, ?, ?, ?)''', 
            (event.type.event_type_id,str(event),event.status.value,event.generator_id(),event.started_dt,event.eta_dt))
        event.event_id = cursor.lastrowid
        task_dict = {}
        for t in event.tasks() :
            task_dict[t.task_name()]=t
            cursor.execute('''insert into event_task 
                (event_id, task_id, task_state, task_status, run_at_dt, updated_dt) 
                values (?, ?, ?, ?, ?, ?)''', 
                (event.event_id,t.task_id(),t.state(),t.status.value,t.run_at_dt,datetime.datetime.utcnow()))
            t.event_task_id =  cursor.lastrowid
        for t in event.tasks() :
            if t.task.depends_on :
                for upstream in t.task.depends_on :
                    cursor.execute('''insert into event_task_prereq 
                                (before_task_id, event_task_id) 
                                values (?, ?)''', 
                                (task_dict[upstream].event_task_id, t.event_task_id))
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
            
            def update_ids(obj_list,name):
                for obj in obj_list:
                    obj_id = None
                    r = list(cursor.execute("select {0}_id, last_seen_in_config_id from {0} where {0}_name = ? and event_type_id = ?".format(name),
                                            (obj.name,event_type.event_type_id)))
                    if len(r) > 1 :
                        raise ValueError('duplicate %s: %s' % name, obj.name)
                    elif len(r) == 1:
                        obj_id = r[0][0]
                        if r[0][1] != config.config_id:
                            cursor.execute("update {0} set last_seen_in_config_id = ? where  {0}_id = ?".format(name),(config.config_id,obj_id))
                    else:
                        cursor.execute("insert into {0} ({0}_name,event_type_id,last_seen_in_config_id) values (?,?,?)".format(name),
                                       (obj.name,event_type.event_type_id,config.config_id))
                        obj_id = cursor.lastrowid
                    setattr(obj,'%s_id' % name, obj_id)
                    
            update_ids(event_type.generators,'generator')
            update_ids(event_type.tasks,'task')
            
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
        started_dt TIMESTAMP not null,
        finished_dt TIMESTAMP ,
        eta_dt TIMESTAMP, 
        updated_dt TIMESTAMP 
        )''' % event.joinEnumsIndices(event.EventStatus,event.MetaStates.all) )
    
        cursor.execute('''CREATE TABLE task (
        task_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        task_name TEXT,
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        cursor.execute('''CREATE TABLE event_task (
        event_task_id INTEGER primary key,
        event_id INTEGER references event(event_id),
        task_id INTEGER references task(task_id),
        task_state TEXT,
        task_status INTEGER CHECK( task_status IN (%s) ) NOT NULL DEFAULT 1,
        run_count INTEGER DEFAULT 0,
        last_run_outcome INTEGER CHECK( last_run_outcome IN (%s) ) NULL DEFAULT NULL,
        updated_dt TIMESTAMP not null,
        run_at_dt TIMESTAMP not null
        )'''% ( event.joinEnumsIndices(event.TaskStatus,event.MetaStates.all),  
                event.joinEnumsIndices(event.RunOutcome,event.MetaStates.all) ) )
   
        cursor.execute('''CREATE TABLE event_task_prereq (
        prereq_id INTEGER primary key,
        before_task_id INTEGER references event_task(event_task_id ),
        event_task_id INTEGER references event_task(event_task_id )
        )''' )
        
        cursor.execute('''CREATE TABLE artifact (
        artifact_id INTEGER primary key,
        event_task_id INTEGER references event_task(event_task_id),
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
        last_changed_dt TIMESTAMP default CURRENT_TIMESTAMP
        )''')
        # Save (commit) the changes
        cursor.execute('insert into settings (settings_id) values (1)')
        #
        conn.commit()
    
        
    
