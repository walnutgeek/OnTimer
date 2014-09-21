ToDo
----

##Done

   * generator schema changes 
   * Generator object
   * Generator.setupEvent
   * Generator.nextEvent
   * Define screens, subscriptions
   * Action matrix
  * db changes
    * rename tables: 
      * task -> task_type, 
      * event_task*->task* 
   
##Now
    * add updated_dt to event and change it on every task update
    * cache superset of u31 and s31
    * implement subscriptions tracker object on server side
    * event summary
    * task summary
    * implement log subscription
  * Screens
    * Screen: Event summary 
    * Screen: Task Screen
    
  
   
##Later 
   * Refactor 
     * websocket connection from javascript (no hard coding) 
   * Subscription
     * [word1 word2] (search in event_string, task_name, generator name)
     * :a[age in days]
     * :e[event_id]
     * :t[event_task_id]
     * :h[event_task_id.run] historical log
     * :l[event_task_id] latest run log
     * :g[generator_id] 
      


| Event         | PAUSE | UNPAUSE | SKIP | CLONE |
|---------------|-------|---------|------|-------|
| active, fail  |  Y    |  N      | Y    |  N    |
| paused        |  N    |  Y      | Y    |  N    |
| success, skip |  N    |  N      | N    |  Y    |
   
| Task                          | PAUSE | UNPAUSE | SKIP | RETRY | RETRY_TREE |
|-------------------------------|-------|---------|------|-------|------------|
| scheduled,running,fail,retry  |  Y    |  N      | Y    |  N    | N          |
| paused                        |  N    |  Y      | Y    |  N    | N          |
| success, skip                 |  N    |  N      | N    |  Y    | Y          |
   
| Generator | SETUP  | RESET   |
|-----------|--------|---------|
| unset     |  Y     |  N      |
| running   |  N     |  N      |
| paused    |  N     |  Y      |
| ontime    |  N     |  Y      |



### Screens

#### Event /e/

s[num_of_days] - scheduled, age calculated by scheduled date 

u[num_of_days] - last updated, age calculated by update date of any tasks in event 

by default all queries assumed to specify u31. 
All tasks that match u31 and s31 will be cached on server any one month worth of event/task data or less
will be served with live updates.
 
e[event_id]

	SELECT 
	e.*, (select event_name from event_type z where e.event_type_id = z.event_type_id) event_name, 
	t.*, (select task_name from task z where t.task_id = z.task_id) task_name
	FROM event_task t, event e   
	where t.event_id = e.event_id 
	and e.event_id = :event_id

E[event_type_id]
 	
 	... 
	and e.event_type_id = :event_type_id
	
g[generator_id]   

    ... 
    and e.generator_id = 2
    
/[any thing after] - free text query

#### Task /t/

t[task_id] particular tasks

##### Tabs
  * T[task_type_id] all tasks of same type
  * l[event_task_id] latest log
  * l[event_task_id]r[run] all previous runs

l[event_task_id] - latest log 

	SELECT a.*, s.* 
	FROM artifact a, artifact_score s, event_task t  
	where s.artifact_id = a.artifact_id  and t.event_task_id = a.event_task_id 
	and t.event_task_id =:event_task_id
	and t.run_count = a.run 

l[event_task_id]r[run] - log from particular run 

	... 
	and :run = a.run 

