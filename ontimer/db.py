import hashlib
import sqlite3
import os
from . import event

default_filename = '.ontimer'

def _conn_decorator(f):
    def magic(self, *args, **kwargs):
        if kwargs.get('conn'):
            return f(self,*args,**kwargs)
        else:
            conn = self.connect()
            try:
                kwargs['conn']=conn
                return f(self,*args,**kwargs)
            finally:
                conn.close()
    return magic

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
        if not(cursor):
            cursor = conn.cursor()
        r = list(cursor.execute(q,params) if params else cursor.execute(q))
        return r

    @_conn_decorator
    def emit_event(self, event, cursor=None, conn=None):
        if not(cursor):
            cursor = conn.cursor()
        self.query('''insert into event 
            (event_type_id,event_string,event_status,generator_id,started_dt,eta_dt) 
            values (?, ?, ?, ?, ?, ?)''', 
            (event.type.event_type_id,str(event),event.status.value,event.generator_id(),event.started_dt,event.eta_dt), cursor=cursor, conn=conn)
        event.event_id = cursor.lastrowid
        task_dict = {}
        for t in event.tasks() :
            task_dict[t.task_name()]=t
            self.query('''insert into event_task 
                (event_id, task_id, task_state, task_status, run_at_dt) 
                values (?, ?, ?, ?, ?)''', 
                (event.event_id,t.task_id(),t.state(),t.status.value,t.run_at_dt), cursor=cursor, conn=conn)
            t.event_task_id =  cursor.lastrowid
        for t in event.tasks() :
            if t.task.depends_on :
                for upstream in t.task.depends_on :
                    self.query('''insert into event_task_prereq 
                                (before_id, after_id) 
                                values (?, ?)''', 
                                (task_dict[upstream].event_task_id, t.event_task_id), cursor=cursor, conn=conn)
        conn.commit()
        return event
        
    @_conn_decorator
    def set_config(self,config_text,conn=None):
        event.Config(config_text)
        r = self.get_config(conn=conn)
        sha1 = hashlib.sha1(config_text).hexdigest()
        if not(r) or r[3] != sha1:
            cursor = conn.cursor()
            self.query("insert into config (uploaded_dt,config_text,config_sha1) values (CURRENT_TIMESTAMP,?,?)",(config_text,sha1),cursor = cursor,conn=conn)
            self.query("update settings set current_config_id = ?, last_changed_dt=CURRENT_TIMESTAMP",(cursor.lastrowid,),cursor = cursor,conn=conn)
            conn.commit()

    @_conn_decorator
    def apply_config(self,conn=None):
        r = self.get_config(conn=conn)
        config = event.Config(r[2])
        config.config_id = r[0]
        cursor = conn.cursor()
        for event_type in config.events:
            r = self.query("select event_type_id, last_seen_in_config_id from event_type where event_name = ?",(event_type.name,),cursor = cursor,conn=conn)
            if len(r) > 1 :
                raise ValueError('duplicate for event_name: %s' % event_type.name)
            elif len(r) == 1:
                event_type.event_type_id = r[0][0]
                if r[0][1] != config.config_id:
                    self.query("update event_type set last_seen_in_config_id = ? where  event_type_id = ?",(config.config_id,event_type.event_type_id),cursor = cursor,conn=conn)
            else:
                self.query("insert into event_type (event_name,last_seen_in_config_id) values (?,?)",(event_type.name,config.config_id),cursor = cursor,conn=conn)
                event_type.event_type_id = cursor.lastrowid
            
            def update_ids(obj_list,name,event_type_id,config_id):
                for obj in obj_list:
                    obj_id = None
                    r = self.query("select {0}_id, last_seen_in_config_id from {0} where {0}_name = ? and event_type_id = ?".format(name),(obj.name,event_type_id),cursor = cursor,conn=conn)
                    if len(r) > 1 :
                        raise ValueError('duplicate %s: %s' % name, obj.name)
                    elif len(r) == 1:
                        obj_id = r[0][0]
                        if r[0][1] != config.config_id:
                            self.query("update {0} set last_seen_in_config_id = ? where  {0}_id = ?".format(name),(config_id,obj_id),cursor = cursor,conn=conn)
                    else:
                        self.query("insert into {0} ({0}_name,event_type_id,last_seen_in_config_id) values (?,?,?)".format(name),(obj.name,event_type_id,config_id),cursor = cursor,conn=conn)
                        obj_id = cursor.lastrowid
                    setattr(obj,'%s_id' % name, obj_id)
                    
            update_ids(event_type.generators,'generator',event_type.event_type_id, config.config_id)
            update_ids(event_type.tasks,'task',event_type.event_type_id, config.config_id)
            
        conn.commit()
        return config
            
    @_conn_decorator
    def get_config(self,config_id=None,conn=None):
        if not(config_id):
            config_id = self.query('select current_config_id from settings', conn=conn)[0][0]
            if not(config_id):
                return None
        return self.query('select config_id,uploaded_dt,config_text,config_sha1 from config where config_id = ?', (config_id,), conn=conn)[0]

    @_conn_decorator
    def create_db(self, conn=None):
        c = conn.cursor()
        
        c.execute('''CREATE TABLE event_type (
        event_type_id INTEGER primary key,
        event_name TEXT, 
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        c.execute('''CREATE TABLE event (
        event_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        event_string TEXT, 
        event_status INTEGER CHECK( event_status IN (%s) ) NOT NULL,
        generator_id INTEGER references generator(generator_id),
        started_dt TIMESTAMP not null,
        finished_dt TIMESTAMP ,
        eta_dt TIMESTAMP 
        )''' % ','.join( str(s.value) for s in event.EventStatus) )
    
        c.execute('''CREATE TABLE task (
        task_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        task_name TEXT,
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        c.execute('''CREATE TABLE event_task (
        event_task_id INTEGER primary key,
        event_id INTEGER references event(event_id),
        task_id INTEGER references task(task_id),
        task_state TEXT,
        task_status INTEGER CHECK( task_status IN (%s) ) NOT NULL DEFAULT 1,
        run_at_dt TIMESTAMP not null
        )'''% ','.join(  str(s.value) for s in event.TaskStatus ) )
   
        c.execute('''CREATE TABLE event_task_prereq (
        prereq_id INTEGER primary key,
        before_id INTEGER references event_task(event_task_id ),
        after_id INTEGER references event_task(event_task_id )
        )''' )
        
        c.execute('''CREATE TABLE artifact (
        artifact_id INTEGER primary key,
        event_task_id INTEGER references event_task(event_task_id),
        name TEXT,
        value TEXT,
        stored_dt TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE artifact_state (
        artifact_state_id INTEGER primary key,
        artifact_id INTEGER references artifact(artifact_id),
        value INTEGER,
        updated_dt TIMESTAMP
        )''')
        
        c.execute('''CREATE TABLE generator (
        generator_id INTEGER primary key,
        event_type_id INTEGER references event_type(event_type_id),
        generator_name TEXT, 
        prev_event_id INTEGER null references event(event_id) ,
        current_event_id INTEGER null references event(event_id),
        last_seen_in_config_id INTEGER references config(config_id)
        )''')
    
        c.execute('''CREATE TABLE config (
        config_id INTEGER primary key,
        uploaded_dt TIMESTAMP,
        config_text TEXT,
        config_sha1 TEXT
        )''')
    
        c.execute('''CREATE TABLE settings (
        settings_id INTEGER primary key CHECK( settings_id in (1) ) default 1,
        current_config_id INTEGER null references config(config_id) default null,
        last_changed_dt TIMESTAMP default CURRENT_TIMESTAMP
        )''')
        # Save (commit) the changes
        c.execute('insert into settings (settings_id) values (1)')
        #
        conn.commit()
    
        
    
