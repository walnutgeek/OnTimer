ToDo
----

##Now
  * restrict file request to server root
  * pypy registration
  * mvp deployment 
   
##Later 
  * implemnet event subscription
  * implement log subscription
  * documentation
  * bitstar 
  * event screen
  * task screen
  * generator screen
  * documentation
    * extract CliServProtocol from todo list into documentation 
	  * Document Client-Server Protocol 
	    * Client can have  N subscriptions from server
	      * MVP will have 1 or 2 subscriptions:
	        * events subscription (always on)
	          { action : 'subscribe',
	            source : 'events',
	            args: { interval-type : 'z' ,
	                    interval-time : '31' ,
	                    event-type : '*' } 
	          }
	        * log subscription (only when run screen is open and displaying live run)
	          { action : 'subscribe',
	            source : 'run',
	            args: { task_id : '382' ,
	                    run_num : '3'   } 
	          }
	    * Client can request data from server:
	      * odd event (event outside of subscription)
	        * { action: 'get', source: 'event', args: { event_id: 35 } }
	        * { action: 'get', source: 'event', args: { task_id: 3 } }
	      * search query (not a priority for MVP, ignore it for now just keep in mind more types of requests)
	        * { action: 'get', source: 'search', args: { q: 'djfl djfld dlfj' } }
	    * Client can request action from server
	      * { action: 'change', source: 'tasks', args: { apply: 'PAUSE', task_id: [ 383, 385, 387 ] } }
    * home page and quick start 
    * convert docs MD into rst
	  * pandoc ?
  * Testing
   * test interaction in phantomjs
   * javascript tests and coverage
   * Subscription cases
     * [word1 word2] (search in event_string, task_name, generator name)
     * :a[age in days]
     * :e[event_id]
     * :t[event_task_id]
     * :h[event_task_id.run] historical log
     * :l[event_task_id] latest run log
     * :g[generator_id] 
  * UI
    * hover over depend_on shows arrows

##Done
  * get log fragment event_id/task_id/run/start/end call
  * display log
  * implement log screen (run screen)
  * send task actions
  * document and implement utils.flatten_liks
  * refactor dropdowns: remove click and navigate to url
    * events url should be: /events/z/31/*
    * dropdowns should dynamically change url
  * design client server protocol able to:
    * to process actions 
    * to implement log subscription 
    * to pull info on events from outside query
  * runs link from event query
  * query screen
    * selected tasks sidebar
    * automatic action bar
  * back button bug
  * Implement swithching between screens
  * design Nav bar,toolbar ad sidebar
  * Bug: history does not refresh if same url provided in push state.
  * implement on sever side globals.meta.TimeVars
  * url scheme
	  * event list url: /events/<filter>?q=<search>
	  * event summary url: /event/3
	  * task summary url: /task/320
	  * log screen url: first log /log/320/0, last: /log/320/-1
   * UI
     * chckbox and link in table
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
     * add updated_dt to event and change it on every task update
     * update db_model.pdf
  * cache superset of u31 and s31 
  * key_group_value
    * write class
    * write tests
      * generic test 
      * kval test
  * documentation 
  	* document and test on ontimer.utils module
  	* learn sphinx
  * data propagation tree subscribers and filters 
  	* design
  	* implementaion
    * implement subscriptions tracker object on server side with data propagation tree.
    * now freeze date
  	* test
  * Consider better name KeyGroupValue
   * Refactor 
     * websocket connection from javascript (no hard coding) 
  * rework page design with bootstrap 
  * documentation 
    * structure skeleton
    * templates for all modules
   
      

