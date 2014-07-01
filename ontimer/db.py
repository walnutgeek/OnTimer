import sqlite3
import os
from . import event

default_filename = '.ontimer'

def dbfile(dir, filename = default_filename):
    return os.path.join(dir, filename)

def db_exists(dir, filename = default_filename):
    return os.path.exists(dbfile(dir,filename=filename))

def connect_db(dir, filename = default_filename):
    conn = sqlite3.connect(dbfile(dir,filename=filename))
    conn.execute('pragma foreign_keys = on')
    return conn
      
def create_db(conn):
    c = conn.cursor()
    
    c.execute('''CREATE TABLE event_type (
    event_type_id int primary key,
    event_name text, 
    last_seen_in_config_id int references config(config_id)
    )''')

    c.execute('''CREATE TABLE event (
    event_id int primary key,
    event_type_id int references event_type(event_type_id),
    event_string text, 
    event_state int CHECK( event_state IN (%s) ) NOT NULL DEFAULT 1,
    generator_id int references generator(generator_id),
    started_dt timestamp not null,
    finished_dt timestamp not null,
    eta_dt timestamp null default null
    )''' % ','.join( str(s.value) for s in event.EventState) )

    c.execute('''CREATE TABLE task (
    task_id int primary key,
    event_type_id int references event_type(event_type_id),
    task_name text
    )''')

    c.execute('''CREATE TABLE event_task (
    event_task_id int primary key,
    event_id int references event(event_id),
    task_id int references task(task_id),
    task_state int CHECK( task_state IN (%s) ) NOT NULL DEFAULT 1,
    run_at_dt timestamp not null
    )'''% ','.join(  str(s.value) for s in event.TaskState ) )
    
    c.execute('''CREATE TABLE event_task_artifact (
    artifact_id int primary key,
    event_task_id int references event_task(event_task_id),
    name text,
    value text,
    stored_dt timestamp
    )''')
    
    c.execute('''CREATE TABLE generator (
    generator_id int primary key,
    event_type_id int references event_type(event_type_id),
    generator_name text, 
    prev_event_id int null references event(event_id) ,
    current_event_id int null references event(event_id)
    )''')

    c.execute('''CREATE TABLE config (
    config_id int primary key,
    uploaded_dt timestamp,
    config_text text,
    config_sha1 text
    )''')

    c.execute('''CREATE TABLE settings (
    settings_id int primary key CHECK( settings_id in (1) ) default 1,
    current_config_id int null references config(config_id) default null,
    last_changed_dt timestamp default CURRENT_TIMESTAMP
    )''')
    # Save (commit) the changes
    c.execute('insert into settings (settings_id) values (1)')
    #
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
    
def load_config():
     pass
