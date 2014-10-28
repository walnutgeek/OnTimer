$(function() {
  var globals = {
    selection : {}
  };

  function process_known_content(json) {
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
      globals.get_event_tasks = json.get_event_tasks
      update_event_table(json.get_event_tasks)
      return true;
    }
    if (json.meta) {
      globals.meta = json.meta;
      globals.EventStatus = $_.utils.BiMap(globals.meta.EventStatus)
      globals.TaskStatus = $_.utils.BiMap(globals.meta.TaskStatus)
      return true;
    }
    return false;
  }

  var table = d3.select("#data_container").append("table").attr('class',
      'gridtable');
  thead = table.append("thead");
  thead_tr = thead.append("tr");

  function update_event_table(events) {
    var column_names = [ 'id', 'name', 'scheduled', 'status', 'run_count',
        'updated', 'depend_on' ];

    var event_group_header = function(d) {
      return [ $_.TCell(d, 'event_string', 2),
          $_.TCell(d, 'scheduled_dt', 1, $_.utils.relativeDateString),
          $_.TCell(d, 'event_status', 1, globals.EventStatus.key),
          $_.TCell(d, undefined, 1),
          $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
          $_.TCell(d, undefined, 1) ];
    };

    var cells_data = function(d) {
      return [ $_.TCell(d, 'task_id', 1), $_.TCell(d, 'task_name', 1),
          $_.TCell(d, 'run_at_dt', 1, $_.utils.relativeDateString),
          $_.TCell(d, 'task_status', 1, globals.TaskStatus.key),
          $_.TCell(d, 'run_count', 1),
          $_.TCell(d, 'updated_dt', 1, $_.utils.relativeDateString),
          $_.TCell(d, 'depend_on', 1) ];
    };

    ths = thead_tr.selectAll("th").data(column_names);
    ths.enter().append("th").text(function(column) {
      return column;
    });
    ths.exit().remove();

    tbody = table.selectAll("tbody").data(events, function(d, i) {
      return i + ':' + d.event_id;
    });

    tbody.enter().append("tbody").append("tr").attr("class", "event_row")
    tbody.exit().remove();

    event_group_ths = tbody.select(".event_row").selectAll("th").data(
        event_group_header);
    event_group_ths.enter().append('th').attr('colspan', function(d) {
      return d.colspan
    });
    event_group_ths.text(function(d) {
      return d.content();
    });

    // append the header row

    // create a row for each object in the data
    var rows = tbody.selectAll(".task_row").data(function(d) {
      return d.tasks;
    }, function(d) {
      return d.task_id;
    });
    rows.enter().append("tr").attr("class", "task_row").on("click", task_click);
    rows.style('background-color', function(t) {
      return globals.selection[t.task_id] ? "#ffffaa" : "#ffffff";
    });
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
    cells.text(function(d) {
      return d.content();
    });
    cells.exit().remove();
  }

  var $container = $('#debug');
  var ws = new WebSocket('ws://'+location.host+'/ws');
  var $message = $('#message');
  ws.onopen = function() {
    $message.attr("class", 'label label-success');
    $message.text('open');
  };
  ws.onmessage = function(ev) {
    $message.attr("class", 'label label-info');
    $message.hide();
    $message.fadeIn("slow");
    $message.text('recieved message');
    setTimeout(function() {
      $message.text('open')
    }, 2000)

    var json = JSON.parse(ev.data)

    if (!process_known_content(json)) {
      // content is unknown just output json
      // visualize(json)
    }
  };
  setInterval(function() {
    if (globals.get_event_tasks)
      update_event_table(globals.get_event_tasks)
  }, 1000 * 60);
  ws.onclose = function(ev) {
    $message.attr("class", 'label label-important');
    $message.text('closed');
  };
  ws.onerror = function(ev) {
    $message.attr("class", 'label label-warning');
    $message.text('error occurred');
  };
});