# OnTimer - Event scheduling and processing

## Functionality

OnTimer is system that generate and process events. For any given event type there is set of 
generators which can emit events of the type and task  which process them. 

### Tasks

Each eventType can have collection of tasks with dependencies between tasks. There are 3 system tasks that 
has special meaning:

| System task     | Description                            |
|------------|----------------------------------------|
| ``begin``  | first task that executed. all tasks that does not specify dependency implicitly depend on ```begin```    |
| ``complete``  | when this task executed, it marks event completed. This task implicitly depend on all end state tasks in the  main flow.  |
| ``eta``  | first task in eta flow. all tasks that does not specify dependency implicitly depend on ```eta``` |

Once completed task produce with success/failure outcome. Upon success depending tasks will be invoked. Failed tasks 
can be set up to retry at later time .

#### Main and ETA flows


Main flow carry out event processing and always get executed. ETA flows carry secondary role in system, 
it help system to recover automatically or notify users about delay. ETA flow will not be executed at all, 
if event completed before ETA time or ETA time was not specified for event. Names of tasks across both 
flows should be unique. ETA's tasks can depend on main flow tasks, but not other way around. Or in other 
words config will be rejected if there are tasks in main flow lists ETA's task as dependency .

All system tasks does not have to be defined in config. By default all system tasks implementation 
is empty (like /bin/true). Once they executed, system tasks will complete with success immediately. 
They still can be defined in config for example to define different implementation. 

If you choose to define ``begin`` and ``eta`` they cannot have any dependencies because they initial 
states in task flow. Contrary ``complete`` can define dependencies and it may be desired if we want 
mark event completed earlier then all tasks in main flow completed successfully. ``complete`` cannot 
depend on ETA flow tasks.


 
### Generators

Event generator emits events based on timer or subscribed event stages. Generator should be able to 
maintain state, to provide ability to hold on creation of next event until previous one achieve completed 
stage.

EventGenerator is not only source of events. Events could be emitted by user input or by tasks itself. 

### API
Python API and command line tool will be provided for tasks to generate events. Tool and API should 
be smart enough to record on which task invocation (event stage) new event was created, so it could 
be presented on UI.

API/command line tool should provide ability for tasks to publish arifacts: files, datasets, 
reports, documents and etc. 


### UI

UI should allow to:
  * Inspect general structure: events, generators, flows. 
  * Ability to navigate history of invocations, event creations, their interdependencies and artifacts created. 
  * Check what events are running, what flows and stages. 
  * Have ability to pause/restart on event, flow, and task level.
  * Inspect initialize and reset state of generator.
  
## Object Design

###EventType 
| member     | Description                            |
|------------|----------------------------------------|
| name       | name of event type (unique)            |
| varDefs    | ordered list of variable definitions (name, datatype, validation rule) |
| generatorDefs | list ```EventGenerator``` definitions |
| flowDefs | list of ```Task``` ```Flow``` definitions |
| validateValues(dict)   | take dictionary and validate according ```varDefs``` |
  
###Event

Holds set of variables defined by eventType

| member     | Description                            |
|------------|----------------------------------------|
| eventType  | ```EventType``` |
| eventKey   | unique auto generated id |
| valueDict  | values for all variables |
| started   | time when event initiated |
| finished   | time when event finished  |
| eta | time when eta flow will be invoked |
| \_\_str\_\_()   | string representation of event like: ```eventType:val1,val2,val3``` |

### EventStage or EventTask

| member     | Description                            |
|------------|----------------------------------------|
| event      | ```Event``` |
| action     | either ```emitted```, ```invoked``` , ```success``` , ```failure```, or ```final``` |
| flowKey    | flow associated |
| taskKey    | task associated |
| occur_dt   | |

### EventGenerator

Event generator emits events based on timer or subscribed event stages. ```emit()``` implentation should be simple, fast, non-blocking code because it runs inside of tornado event loop.

| member      | Description                            |
|------------|----------------------------------------|
| enentType | ```EventType``` it creates |
| name | generator name |
| timer      | [OnExp](OnExp.md) to specify when event is generated |
| subscribedOn  | values for all variables |
| emit()      | method that returns newly emitted events. only called when conditions (timer, subscribed events) are met. |

###Flow
  DAG of tasks, invoked by event.
  
| member    | Description                            |
|-----------|----------------------------------------|
| enentType | ```EventType``` |
| key       | name of flow   (unique)                |
| tasks     | list of tasks objects                  |
  
 
###Task

| member   | Description                            |
|----------|----------------------------------------|
| flowKey  | name of flow                           |
| taskKey  | values for all variables               |
| dependOn | task in same flow                      |
| runner   | Runner                                 | 


### Runner
specify how to run task and measure success or failure

| member    | Description                            |
|-----------|----------------------------------------|
| run()     | runs task                              |

### ProcessRunner

| member       | Description |
|--------------|----------------------------------------|
| cmd_template | converts event data into command line to be executed by ```run()``` |
| run()        | runs task  |


## Config (yaml)
```yaml
events:
  - name: returns
```


 

