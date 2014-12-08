$(function() {
	
  var globals = {
    selection : {}
  };

  var History = window.History;
  $(document).on('click', '.history_nav', function(e) {
      var urlPath = $(this).attr('href');
      var title = $(this).text();
      History.pushState({time: new Date()}, null, urlPath);
      return false; // prevents default click action of <a ...>
  });
  
  function history_nav(href,text){
    return '<a href="/'+href+'" class="history_nav">'+text+'</a>';
  }
  
  function a(screen){
    return function(cell){
      return history_nav( screen+'/'+cell, cell);
    }
  }

  var renderers = {
      events: {
        init: function() {
          this.data_container = d3.select("#data_container");
          this.data_container.html('');
          this.table = this.data_container.append("table").attr('class', 'gridtable');
          this.thead = this.table.append("thead");
          this.thead_tr = this.thead.append("tr");
          var column_names = [ '', 'id', 'name', 
                               'scheduled', 'status', 'run_count',
                               'updated', 'depend_on' ];
  

          var ths = this.thead_tr.selectAll("th").data(column_names);
          ths.enter().append("th").text(function(column) {
            return column;
          });
          ths.exit().remove();


        },
        dispatch: function(json) {
          if (json.get_event_tasks) {
            globals.events = {}
            globals.tasks = {}
            json.get_event_tasks.forEach(function(ev) {
              globals.events[ev.event_id] = ev;
              ev.tasks.forEach(function(t) {
                globals.tasks[t.event_task_id] = t;
              })
            });
            for ( var key in globals.selection) {
              if (globals.selection.hasOwnProperty(key)
                  && !globals.tasks.hasOwnProperty(key)) {
                delete globals.selection[key];
              }
            }
            globals.get_event_tasks = json.get_event_tasks;
            this.data =  json.get_event_tasks;
            this.refresh();
            return true;
          }
        },
        refresh: function() {
          if( !this.data ) return;
          console.log(this.data.length);
          function none(){return '';};
          function checkbox(v){ return '<input type="checkbox" class="task_select" value="'+v+'" />'; }
          
          var event_group_header = function(d) {
            return [ 
                    $_.TCell(d, 'event_id', 1 , none),
                $_.TCell(d, 'event_id', 1 , a('event')),
                $_.TCell(d, 'event_string', 1),
                $_.TCell(d, 'scheduled_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'event_status', 1, globals.EventStatus.key),
                $_.TCell(d, undefined, 1),
                $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, undefined, 1) ];
          };

          var cells_data = function(d) {
            return [ 
                    $_.TCell(d, 'task_id', 1 , checkbox ), 
                     $_.TCell(d, 'task_id', 1 , a('task')), 
                     $_.TCell(d, 'task_name', 1, function(cell,d){
                       return history_nav('events/T'+d.task_type_id, cell);
                     }),
                $_.TCell(d, 'run_at_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'task_status', 1, globals.TaskStatus.key),
                $_.TCell(d, 'run_count', 1),
                $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'depend_on', 1) ];
          };

          var tbody = this.table.selectAll("tbody").data(this.data, function(d, i) { return i + ':' + d.event_id; } );

          tbody.enter().append("tbody").append("tr").attr("class", "event_row")
          tbody.exit().remove();

          var event_group_ths = tbody.select(".event_row").selectAll("th").data(
              event_group_header);
          event_group_ths.enter().append('th').attr('colspan', function(d) {
            return d.colspan
          });
          event_group_ths.html(function(d) {
            return d.content();
          });
          // append the header row
          
          // create a row for each object in the data
          var rows = tbody.selectAll(".task_row").data(function(d) {
            return d.tasks;
          }, function(d) {
            return d.task_id;
          });
          rows.enter().append("tr").attr("class", "task_row")
          //.on("click", task_click);
//            rows.style('background-color', function(t) {
//              return globals.selection[t.task_id] ? "#ffffaa" : "#ffffff";
//            });
          rows.exit().remove();

          function task_click(t) {
            if (globals.selection[t.task_id]) {
              delete globals.selection[t.task_id];
            } else {
              globals.selection[t.task_id] = true;
            }
            update_event_table(globals.get_event_tasks);
          }

          // create a cell in each row for each column
          var cells = rows.selectAll("td").data(cells_data);
          cells.enter().append("td");
          cells.html(function(d) {
            return d.content();
          });
          cells.exit().remove();
        }
      },
      event: {
        init: function() {
            var data_container = d3.select("#data_container");
            data_container.html('');
        },
        dispatch: function() {},
        refresh: function() {}
      },
      task: {
        init: function() {
          var data_container = d3.select("#data_container");
          data_container.html('');
        },
        dispatch: function() {},
        refresh: function() {}
      },
      log: {
        init: function() {
          var data_container = d3.select("#data_container");
          data_container.html('');
        },
        dispatch: function() {},
        refresh: function() {}
      }
  };
  
  var render = 'events';
  var state ;
  
  function rr(){return renderers[render];}
  
  var updateContent = function(State) {
    state = $_.utils.splitUrlPath(State.hash)
    var key = state.path.length > 1 ? state.path[1] : 'events' ;
    console.log(JSON.stringify(state));
    if(renderers[key]){
      render = key;
      rr().init();
    }
    rr().refresh();
  };
  
  function process_known_content(json) {
    if(rr().dispatch(json)){
      return true;
    }
    
    if (json.meta) {
      globals.meta = json.meta;
      globals.EventStatus = $_.utils.BiMap(globals.meta.EventStatus);
      globals.TaskStatus = $_.utils.BiMap(globals.meta.TaskStatus);
      globals.event_types = { 
    	  value : '*',
    	  choices : globals.meta.EventTypes
      };
      globals.interval={
    		  type: { 
    			  value : 'z' ,
    		      choices :  globals.meta.TimeVars 
    		  },
              time: { 
            	  value : 1,
            	  choices : { 
            		  1: '1 day ago',
            		  2: '2 days ago',
            		  3: '3 days ago',
            		  7: '1 week ago',
            		  31: '1 month ago' }
              }
      };
      
      function update_dropdown(id,data,prefix){
    	  prefix = prefix || '';
    	  $('#'+id+' .last-selected').text(prefix+data.choices[data.value]);
    	  var ddm =$('#'+id+' .dropdown-menu');
    	  ddm.empty();
    	  for (var key in data.choices) {
			  if (data.choices.hasOwnProperty(key)) {
			    ddm.append( '<li><a href="#" data-value="'+key+'">'+data.choices[key]+'</a></li>' );
			  }
		  }
    	  $('#'+id+' .dropdown-menu li a').click(function(event){
    		  data.value=event.target.attributes["data-value"].value;
    		  $('#'+id+' .last-selected').text(prefix+data.choices[data.value]);
              $(this).closest(".dropdown-menu").prev().dropdown("toggle");
    		  return false; 
    	  });
    	  
      }
      update_dropdown('interval-type',globals.interval.type);
      update_dropdown('interval-time',globals.interval.time);
      update_dropdown('event-type',globals.event_types,'Events: ');
      
      return true;
    }
    return false;
  }
  
  

  // Content update and back/forward button handler
  History.Adapter.bind(window, 'statechange', function() {
      updateContent(History.getState());
  }); 
  State = History.getState();
  History.pushState({urlPath: window.location.pathname, time: new Date()}, $("title").text(), location.url);

  $('#submit').click(function(event){
	  var u = '/events/'+globals.interval.type.value + globals.interval.time.value;
	  if( globals.event_types.value !== '*'){
		  u+='e'+globals.event_types.value;
	  }
	  var search = $('#search').val();
	  if( search !== '' ){
		  u+='?q='+encodeURI(search);
	  }
	  History.pushState({time: new Date()}, null, u);
	  return false;
  });
  

  function connect(){
    var $container = $('#debug');
    var $message = $('#message');
    var ws = new WebSocket('ws://'+location.host+'/ws');
    ws.onopen = function() {
      $message.text("On");
      $message.attr("class", 'label label-info');
    };
    
    ws.onmessage = function(ev) {
      $message.attr("class", 'label label-success');
      $message.text("On");
      $message.fadeIn("slow");
      setTimeout(function() {
        $message.attr("class", 'label label-info');
      }, 1000)
  
      var json = JSON.parse(ev.data)
  
      if (!process_known_content(json)) {
        // content is unknown just output json
        // visualize(json)
      }
    };
    
    ws.onclose = function(ev) {
      $message.text("Off");
      $message.attr("class", 'label label-danger');
      ws.dead=true;
    };
    ws.onerror = function(ev) {
      $message.attr("class", 'label label-warning');
    };
    ws.dead=false;
    return ws;
  }
  var ws = connect();
  
  setInterval(function() {
    if( ws.dead ){
      ws = connect();
    }else if (globals.get_event_tasks)
      rr().refresh();
  }, 1000 * 60);
});