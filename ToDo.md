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
   
##Now
  * data propagation tree subscribers and filters 
  	* design
  	* implementaion
    * implement subscriptions tracker object on server side with data propagation tree.
  * event summary
  * task summary
  * implement log subscription
  * Screens
    * Screen: Event summary 
    * Screen: Task Screen
  * documentation 
    * structure skeleton
    * templates for all modules
    * home page and quick start 
   
##Later 
  * Consider better name KeyGroupValue
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
      

