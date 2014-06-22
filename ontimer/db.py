import sqlite3
from . import event

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
    started_dt timestamp not null,
    finished_dt timestamp not null,
    eta_dt timestamp null default null
    )''' % (','.join( ( str(s.value) for s in event.EventState) )))

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
    )'''% (','.join( ( str(s.value) for s in event.TaskState) )))
    
    c.execute('''CREATE TABLE event_task_artifact (
    artifact_id int primary key,
    event_task_id int references event_task(event_task_id),
    json_value text,
    stored_dt timestamp
    )''')
    
    c.execute('''CREATE TABLE generator (
    generator_id int primary key,
    event_type_id int references event_type(event_type_id),
    generator_name text
    )''')

    c.execute('''CREATE TABLE generator_state (
    generator_state_id int primary key,
    generator_id int references generator(generator_id),
    event_id int references event(event_id)
    )''')

    c.execute('''CREATE UNIQUE INDEX generator_state_xref 
    ON generator_state (generator_id,event_id) ''')

    c.execute('''CREATE TABLE config (
    config_id int primary key,
    uploaded_dt timestamp,
    config_text text,
    config_sha1 text
    )''')

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()