# Minimal Viable Product

## Goals

Build system that generate and process events. For any given event type there is set of 
generators which can emit events of the type and task flows which process them. Flow is collection of tasks with 
dependencies between tasks within flow. Flow can be view directed acyclic graph with task as nodes and dependencies as edges. 
There is no dependencies pointing outside of the flow. Outside dependencies have to be handled thru event generators by 
emitting new events. Generators should be able to subscribe to event stages. Generator should be able to maintain state, to provide ability 
to hold on creation of next event until previous one achieve certain stage.

EventGenerator is not only source of events. Events could be emitted by user input or by tasks itself. 

Python API and command line tool will be provided for tasks to generate events. Tool and API should be smart enough 
to record on which task invocation (event stage) new event was created, so it could be presented on UI.

API/command line tool should provide ability for tasks to publish arifacts: stdout, stderr, datasets, reports, documents and etc. 

UI should allow to:
  * Inspect general structure: events, generators, flows. 
  * Ability to navigate history of invocations, event creations, their interdependencies and artifacts created. 
  * Check what events are running, what flows and stages. 
  * Have ability to pause/restart on event, flow, and task level.
  * Inspect initialize and reset state of generator.
  
## Design

###EventType 
| member     | Description                            |
|------------|----------------------------------------|
| name       | name of event type (unique)            |
| varDefs    | ordered list of variable definitions (name, datatype, validation rule) |
| generatorDefs | list ```EventGenerator``` definitions |
| flowDefs | list of ```Task``` ```Flow``` definitions |
| validateValues(dict)   | take dictionary and validate according ```varDefs``` |
  
###Event

Holds set of variables specific to eventType

| member     | Description                            |
|------------|----------------------------------------|
| eventType  | ```EventType``` |
| eventKey   | unique auto generated id               |
| valueDict  | values for all variables               |
| \_\_str\_\_()   | string representation of event like: ```eventType:val1,val2,val3``` |

### EventStage

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

### OsCmdRunner

| member       | Description |
|--------------|----------------------------------------|
| cmd_template | converts event data into command line to be executed by ```run()``` |
| run()        | runs task  |


## Config (yaml)
```yaml
events:
  - name: returns
```


 

