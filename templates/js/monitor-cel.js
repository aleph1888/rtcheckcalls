/*************************************************
 * Dom helpers
 */

function write_div(text, div_id) {
	$('<div>'+text+'</div>', {
		id:'foo',
		text: text}).appendTo(div_id).hide().fadeIn().delay(45000).slideUp()
}

function clear_events() {
	$('#cel_events').children().fadeOut(300, function() {$(this).remove()})
}

function do_ping() {
	console.log("ping")
	$.get("/")
	setTimeout('do_ping()',60000);
}

events_head = false
current_linkedid = null
total_events = 0
function fill_head(data) {
	var text = "<tr>"
	for (variable in data) {
		text += "<td>"+variable+"</td>";
	}
	text += "</td>"
	var node = $(text);
	node.stamp = data.linkedid
	node.data('stamp', data.linkedid)
	$('#cel_events_head').html(node.fadeIn())
	events_head = true
	
}


function show_all() {
	$('#current_linkedid').html('all')
	$('#cel_events').children().fadeIn()
	current_linkedid = null
}

function show_linkedid(linkedid) {
	current_linkedid = linkedid;
	$('#current_linkedid').html(current_linkedid)
	$.each($('#cel_events').children(), function(index, elmt) {
		if ($(elmt).data('linkedid') == current_linkedid) {
			$(elmt).fadeIn()
		}
		else {
			$(elmt).fadeOut()
		}
	})
}

function on_event(data) {
	delete data.amaflags
	if (!events_head) {
		fill_head(data)
	}
	var text = "<tr>"
	for (variable in data) {
		if (variable == 'linkedid') {
			text += "<td><a href='javascript:show_linkedid(\""+data[variable]+"\")'>"+data[variable]+"</a></td>";
		}
		else {
			text += "<td>"+data[variable]+"</td>";
		}
	}
	text += "</td>"
	var node = $(text);
	node.data('linkedid', data.linkedid)
	if ((current_linkedid == null) || (current_linkedid == data.linkedid)) {
		$('#cel_events').prepend(node.fadeIn())
	} else {
		node.css('display', 'none').prependTo('#cel_events')
	}
	total_events += 1
	$('#total_events').html(total_events)
	
}

/*************************************************
 * Register events once document is ready
 */
$(document).ready( function () {
	/*paper = Raphael("canvas", 640, 480),
	root_circle = paper.circle(320, 240, 60).animate({fill: "#223fa3", stroke: "#000", "stroke-width": 80, "stroke-opacity": 0.5}, 2000, "backOut");*/

	if (!!window.EventSource) {
	  setTimeout('do_ping()',60000);
	  var source = new EventSource('/sse');
	} else {
	  // Result to xhr polling :(
	}
	source.addEventListener('message', function(e) {
		write_div(e.data, '#bla')
	}, false);

	source.addEventListener('callmonitor', function(e) {
	//	var data = JSON.parse(e.data);
	}, false);
	source.addEventListener('credit', function(e) {
		var data = JSON.parse(e.data);
		write_div(e.data, '#default')
	}, false);

	source.addEventListener('peers', function(e) {
		var data = JSON.parse(e.data);
	}, false);

	source.addEventListener('peer', function(e) {
		var peer_event = JSON.parse(e.data);
	}, false);


	source.addEventListener('rtcheckcalls', function(e) {
		var data = JSON.parse(e.data);
		on_event(data)
	}, false);

	source.addEventListener('open', function(e) {
		write_div('connection started', '#default')
	}, false);

	source.addEventListener('channels', function(e) {
		//write_div(e.data, '#default')

	}, false);

	source.addEventListener('error', function(e) {
	  if (e.readyState == EventSource.CLOSED) {
	        // Connection was closed.
		write_div('connection closed', '#default')
	  }
	}, false);
} ); // document.load

