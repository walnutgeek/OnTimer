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
	    	scheduled after dt_delta(hours=-24)
	    	event_id = N
	    	event_type = S  and scheduled after dt_delta(days=-31)
	    	gnerator_id = G and scheduled after dt_delta(days=-31)
	    	event_string ~ Q and scheduled after dt_delta(days=-31)
   * Subscription
     * Events<query>
     * Task<Task_ID>
     * Log<Task_ID>
      
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
   



