ToDo
----

##Done

   * generator schema changes 
   * Generator object
   * Generator.setupEvent
   * Generator.nextEvent
   
##Now
   * Define screens, subscriptions
   * Action matrix
   
##Later 
   * Reusable components
     * Event Filter
  		* Cases   
	     	* Recent +-24hr events (refactor to use event filter)
	        * Event filter: Search event
	    * query 
	    	scheduled after dt_delta(days=-1)
	    	event_id = N
	    	event_type = S and scheduled after dt_delta(days=-31)
	    	gnerator_id = G and scheduled after dt_delta(days=-31)
	    	event_string ~ Q and scheduled after dt_delta(days=-31)
	    	
   * Subscription
     * q:[query] 
     * e[event_id]
     * t[event_task_id]
     * l[log_id]
     * g[generator_id]
      
   * Screens
     * Screen: Event summary 
        * Event filter: Recent +-24hr events (refactor to use event filter)
        * Event filter: Search event
     * Screen: Task Screen
     	* Task info
     	* Logs
     * Screen: Generator
        * Event Filter events that
   * Refactor 
     * websocket connection from javascript (no hard coding) 


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
   
| Generator                     | SETUP  | RESET   |
|-------------------------------|--------|---------|
| UNSET                         |  Y     |  N      |
| EVENT_RUNNING                 |  N     |  N      |
| PAUSED                        |  N     |  Y      |
| ONTIME                        |  N     |  Y      |


