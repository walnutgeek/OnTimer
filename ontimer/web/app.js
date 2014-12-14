$(function() {
	
  var globals = {
    selection : {},
    data_is_ready: function(){ return this.get_event_tasks; }
  };
  
//  | Task                          | PAUSE | UNPAUSE | SKIP | RETRY | RETRY_TREE |
//  |-------------------------------|-------|---------|------|-------|------------|
//  | scheduled,running,fail,retry  |  Y    |  N      | Y    |  N    | N          |
//  | paused                        |  N    |  Y      | Y    |  N    | N          |
//  | success, skip                 |  N    |  N      | N    |  Y    | Y          |

  var task_actions = {
      PAUSE: ['scheduled','running','fail','retry'],
      UNPAUSE: ['paused'],
      SKIP: ['scheduled','running','fail','retry','paused'],
      RETRY: ['success','skip'],
      RETRY_TREE: ['success', 'skip'],
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

  function update_sidebar_and_actions(){
    if( ! $_.utils.size(globals.selection) ){
      $('#sidebar').empty();
      $('#actions').hide();
    }else{
      var statuses = {};
      for ( var key in globals.selection) {
        if (globals.selection.hasOwnProperty(key)){
          var task = globals.tasks[key];
          var task_status = globals.bimapTaskStatus.key(task.task_status);
          if( ! statuses[task_status] ){
            statuses[task_status] = [];
          }
          statuses[task_status].push(task);
        }
      }
      $('#sidebar').html('<div id="selected_tasks"> Selected:<dl></dl></div>');
      for ( var s in statuses) {
        $('#selected_tasks dl').append('<dt>'+s+'</dt><dd>'
            +$_.utils.join(statuses[s],',',function(t){
              return t.task_name+'('+t.task_id+')'; })+'</dd>');
      }
      var form = $('#actions div form').empty();
      for( var act in task_actions ){
        var disabled = '';
        for ( var s in statuses) {
          if(task_actions[act].indexOf(s)===-1){
            disabled = ' disabled';
            break;
          }
        }
        form.append(' <button type="submit" class="btn'+disabled+'" id="'+act+'">'+act+'</button>');
      }
      $('#actions').show();
    }
  }
  

  $(document).on('change', '.task_select', function(){
    if( this.checked ) {
      globals.selection[this.value] = true;
    }else{
      delete globals.selection[this.value];
    }
    update_sidebar_and_actions();
  });

  var currScreen = 'wait';
  
  function rr(){return globals.renderers[currScreen];}
  
  function updateContent(State) {
    var prevScreen = currScreen;
    var state = $_.utils.splitUrlPath(State.hash);
    delete state.variables['_suid'];
    if ( state.path.length  < 2 || !state.path[1]){
      state = $_.utils.splitUrlPath('/events/');
    }
    var key = state.path[1] ;
    if(globals.renderers[key]){
      currScreen = key;
    }
    if( !globals.data_is_ready() ){
      currScreen = 'wait';
    }
    rr().state=state;
    if( prevScreen != currScreen ) {
      rr().init();  
    }
    if( currScreen !== 'wait' ){
      rr().refresh();
    }
  };
  
  var History = window.History;
  $(document).on('click', '.history_nav', function(e) {
      var urlPath = $(this).attr('href');
      var title = $(this).text();
      History.pushState({time: new Date()}, null, urlPath);
      return false; // prevents default click action of <a ...>
  });
  History.Adapter.bind(window, 'statechange', function() {
    updateContent(History.getState());
  }); 


  
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

  function history_nav(href,text){
    return '<a href="/'+href+'" class="history_nav">'+text+'</a>';
  }
  
  function a(screen){
    return function(cell){
      return history_nav( screen+'/'+cell, cell);
    }
  }

  function none(){return '';};
  
  function checkbox(v){ return '<input type="checkbox" class="task_select" value="'+v+'" '+ (globals.selection[v] ? 'checked' : '') +'/>'; }

  function update_navbar(event,task,run){
    if(!event){
      $('#query_dropdowns').show();
      $('#crumbs').hide();
    }else{
      $('#query_dropdowns').hide();
      $('#crumbs').show();
      $('#query_li').show().removeClass('active');
      $('#query_li a').attr('href', globals.renderers['events'].state.toString());
      $('#type_li').show().removeClass('active');
      $('#type_li a').attr('href', '/events/'+globals.interval.type.value + globals.interval.time.value +"T" + event.event_type_id).text(event.event_name);
      $('#event_li').show();
      var i = event.event_string.indexOf(',');
      $('#event_li a').text(i >=0 ? event.event_string.substr(i+1) : '---' ).attr('href', '/event/'+event.event_id);
      if ( !task ){
        $('#event_li').addClass('active');
        $('#task_li').hide();
        $('#run_li').hide();
      }else{
        $('#event_li').removeClass('active');
        $('#task_li').show().addClass('active');
        $('#task_li a').text(task.task_name);
        if( !run ){
          $('#run_li').hide();
          $('#task_li').addClass('active');
        }else{
          $('#task_li').removeClass('active');
          $('#run_li').show().addClass('active');;
          data = { value : run.run, choices : {}}
          for (i = 1; i <= task.run_count; i++) { 
            data.choices[i]='#'+i;
          }
          update_dropdown('run_li',data);
        }
      }
    }
  }
  
  globals.renderers = {
      wait: {
        init: function() {
          update_navbar();
          this.data_container = d3.select("#data_container");
          this.data_container.html('<span class="glyphicon glyphicon-time"></span> Please Wait....');
        },
        refresh: function(){
          updateContent(History.getState());
        }
      },
      events: {
        state: $_.utils.splitUrlPath("/events/z1"),
        init: function() {
          update_navbar();
          this.data_container = d3.select("#data_container");
          this.data_container.html('');
          this.table = this.data_container.append("table").attr('class', 'gridtable');
          this.thead = this.table.append("thead");
          this.thead_tr = this.thead.append("tr");
          var column_names = [ '', 'id', 'name',  'scheduled', 'status', 'run_count', 'updated', 'depend_on' ];

          var ths = this.thead_tr.selectAll("th").data(column_names);
          ths.enter().append("th").text(function(column) {
            return column;
          });
          ths.exit().remove();
        },
        refresh: function() {
          if( !globals.get_event_tasks  ) return;
          if( !this.table ) this.init();
          
          var event_group_header = function(d) {
            return [ 
                $_.TCell(d, 'event_id', 1 , none),
                $_.TCell(d, 'event_id', 1 , a('event')),
                $_.TCell(d, 'event_string', 1),
                $_.TCell(d, 'scheduled_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'event_status', 1, globals.bimapEventStatus.key),
                $_.TCell(d, undefined, 1),
                $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, undefined, 1) ];
          };

          var cells_data = function(d) {
            return [ 
                $_.TCell(d, 'task_id', 1 , checkbox ), 
                $_.TCell(d, 'task_id', 1 , a('task')), 
                $_.TCell(d, 'task_name', 1, function(cell,d){ return history_nav('events/T'+d.task_type_id, cell); }),
                $_.TCell(d, 'run_at_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'task_status', 1, globals.bimapTaskStatus.key),
                $_.TCell(d, 'run_count', 1, function(cell,d){ return history_nav('run/'+d.task_id +'/'+cell, cell); }),
                $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
                $_.TCell(d, 'depend_on', 1) ];
          };

          var tbody = this.table.selectAll("tbody").data(globals.get_event_tasks, function(d, i) { return i + ':' + d.event_id; } );

          tbody.enter().append("tbody").append("tr").attr("class", "event_row")
          tbody.exit().remove();

          var event_group_ths = tbody.select(".event_row").selectAll("th").data(
              event_group_header);
          event_group_ths.enter().append('th').attr('colspan', function(d) {
            return d.colspan;
          });
          event_group_ths.html(function(d) {
            return d.content();
          });

          var rows = tbody.selectAll(".task_row").data(function(d) {
            return d.tasks;
          }, function(d) {
            return d.task_id;
          });
          rows.enter().append("tr").attr("class", "task_row");
          rows.exit().remove();
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
          var event_id = Number(this.state.path[2]) ;
          var event = globals.events[event_id];
          console.log(event);
          update_navbar(event);
          var data_container = d3.select("#data_container");
          data_container.html('');
        },
        refresh: function() {}
      },
      task: {
        init: function() {
          var task_id = Number(this.state.path[2]) ;
          var task = globals.tasks[task_id];
          var event = globals.events[task.event_id];
          console.log(event,task);
          update_navbar(event,task);
          var data_container = d3.select("#data_container");
          data_container.html('');
        },
        refresh: function() {}
      },
      run: {
        init: function() {
          var task_id = Number(this.state.path[2]) ;
          var run_num = this.state.path[3] ;
          var task = globals.tasks[task_id];
          var event = globals.events[task.event_id];
          console.log(event,task);
          update_navbar(event,task,{run: Number(run_num)});
          var data_container = d3.select("#data_container");
          data_container.html('');
        },
        refresh: function() {}
      }
  };
  
  
  function refresh_dropdowns() {
    
    globals.bimapEventStatus = $_.utils.BiMap(globals.meta.EventStatus);
    globals.bimapTaskStatus = $_.utils.BiMap(globals.meta.TaskStatus);
    globals.bimapEventTypes = $_.utils.BiMap(globals.meta.EventTypes);
    
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
    
    update_dropdown('interval-type',globals.interval.type);
    update_dropdown('interval-time',globals.interval.time);
    update_dropdown('event-type',globals.event_types,'Events: ');
    update_sidebar_and_actions();
  }
  
  function process_content(json) {
    var refresh = false;
    if (json.get_event_tasks) {
      globals.events = {}
      globals.tasks = {}
      json.get_event_tasks.forEach(function(ev) {
        globals.events[ev.event_id] = ev;
        ev.tasks.forEach(function(t) {
          globals.tasks[t.task_id] = t;
        })
      });
      for ( var key in globals.selection) {
        if (globals.selection.hasOwnProperty(key)
            && !globals.tasks.hasOwnProperty(key)) {
          delete globals.selection[key];
        }
      }
      globals.get_event_tasks = json.get_event_tasks;
      refresh = true;
    }
    if (json.meta) {
      globals.meta = json.meta;
      refresh_dropdowns();
    }
    return refresh;
  }


  
  
  

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
      if ( process_content(json) ){
        rr().refresh();
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
    }else if ( globals.data_is_ready() )
      rr().refresh();
  }, 1000 * 30);
  
  History.pushState({urlPath: window.location.pathname, time: new Date()}, $("title").text(), location.url);
});