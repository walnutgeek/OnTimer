ToDo
----

##Now
  * event screen
  * task screen
  * log screen
  	* implement log subscription
   
##Later 
  * documentation
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
   
      

