import sqlite3

def create_db(dbpath):
    conn = sqlite3.connect(dbpath)
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
    emitted_dt timestamp
    )''')

    c.execute('''CREATE TABLE event_stage (
    event_stage_id int primary key,
    event_id int references event(event_id),
    flow_key text,
    task_key text,
    occur_dt timestamp
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
