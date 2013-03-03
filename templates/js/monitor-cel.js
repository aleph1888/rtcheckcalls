/*************************************************
 * Dom helpers
 */

function write_div(text, div_id) {
	$('<div>'+text+'</div>', {
		id:'foo',
		text: text}).appendTo(div_id).hide().fadeIn().delay(45000).slideUp()
}

events_head = false
function fill_head(data) {
	var text = "<tr>"
	for (variable in data) {
		text += "<td>"+variable+"</td>";
	}
	text += "</td>"
		$('#cel_events_head').html(text)
	events_head = true
	
}
function on_event(data) {
	delete data.amaflags
	if (!events_head) {
		fill_head(data)
	}
	var text = "<tr>"
	for (variable in data) {
		text += "<td>"+data[variable]+"</td>";
	}
	text += "</td>"
		$('#cel_events').prepend(text)
	
}

/*************************************************
 * Register events once document is ready
 */
$(document).ready( function () {
	/*paper = Raphael("canvas", 640, 480),
	root_circle = paper.circle(320, 240, 60).animate({fill: "#223fa3", stroke: "#000", "stroke-width": 80, "stroke-opacity": 0.5}, 2000, "backOut");*/

	if (!!window.EventSource) {
	  var source = new EventSource('/sse');
	} else {
	  // Result to xhr polling :(
	}
	source.addEventListener('message', function(e) {
		write_div(e.data, '#bla')
	}, false);

	source.addEventListener('callmonitor', function(e) {
		var data = JSON.parse(e.data);
		//write_div(e.data, '#default')
	}, false);
	source.addEventListener('credit', function(e) {
		console.log(e.data);
		var data = JSON.parse(e.data);
	}, false);

	source.addEventListener('peers', function(e) {
		var data = JSON.parse(e.data);
	}, false);

	source.addEventListener('peer', function(e) {
		var peer_event = JSON.parse(e.data);
		console.log(peer_event)
	}, false);


	source.addEventListener('rtcheckcalls', function(e) {
		console.log(e.data);
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

