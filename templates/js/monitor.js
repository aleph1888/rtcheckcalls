// Unavailable states
var UNAVAILABLE = Array('UNKNOWN', 'UNREACHABLE');

ICON_CLOUD = 'M24.345,13.904c0.019-0.195,0.03-0.392,0.03-0.591c0-3.452-2.798-6.25-6.25-6.25c-2.679,0-4.958,1.689-5.847,4.059c-0.589-0.646-1.429-1.059-2.372-1.059c-1.778,0-3.219,1.441-3.219,3.219c0,0.21,0.023,0.415,0.062,0.613c-2.372,0.391-4.187,2.436-4.187,4.918c0,2.762,2.239,5,5,5h15.875c2.762,0,5-2.238,5-5C28.438,16.362,26.672,14.332,24.345,13.904z';

ICON_LOCK = Raphael.transformPath('M24.875,15.334v-4.876c0-4.894-3.981-8.875-8.875-8.875s-8.875,3.981-8.875,8.875v4.876H5.042v15.083h21.916V15.334H24.875zM10.625,10.458c0-2.964,2.411-5.375,5.375-5.375s5.375,2.411,5.375,5.375v4.876h-10.75V10.458zM18.272,26.956h-4.545l1.222-3.667c-0.782-0.389-1.324-1.188-1.324-2.119c0-1.312,1.063-2.375,2.375-2.375s2.375,1.062,2.375,2.375c0,0.932-0.542,1.73-1.324,2.119L18.272,26.956z', 's0.5,0.5t8,0')

// Raphael canvas
var paper;

// Root canvas circle
var root_circle;
var root_text = Array()

// Calls dictionary
var calls = {}

// Channels
var all_channels = {'channels':{}, 'local':{}}

// Floating elements
var floats = Array();


/*************************************************
 * Dom helpers
 */

function write_div(text, div_id) {
	$('<div>'+text+'</div>', {
		id:'foo',
		text: text}).appendTo(div_id).hide().fadeIn().delay(45000).slideUp()
}


/*************************************************
 * Leg Management
 */

function connect_legs(elmt, involved) {
	var part1 = involved[0];
	var part2 = involved[1];
	var diff_x;
	var diff_y;
	if (part1.x < part2.x) {
		diff_x = part2.x+20;
	}
	else {
		diff_x = part2.x-20;
	}
	if (part1.y < part2.y) {
		diff_y = part2.y+20;
	}
	else {
		diff_y = part2.y-20;
	}

	var path = [["M", part1.x, part1.y], ["S", diff_x, diff_y, part2.x, part2.y]];
	var path_node;
	if (floats['path'+part1.name+part2.name]) {
		path_node = floats['path'+part1.name+part2.name];
		path_node.remanence += 0.1;
		var path_string = "M"+part1.x+" "+part1.y+"S"+diff_x+" "+diff_y+" "+part2.x+" "+part2.y;
		path_node.animate({stroke: '#FFF', "stroke-width": 4, "stroke-linecap": "round", "opacity": 0.7, path: path_string});
	}
	else {
		path_node = paper.path(path);
		path_node.remanence = 0.2;
		path_node.attr({stroke: '#FFF', "stroke-width": 4, "stroke-linecap": "round", "opacity": 0.7});
	}
	path_node.toFront();
	path_node.mouseover(function() { path_node.animate({"stroke-width": 6}, 1000) });
	path_node.mouseout(function() { path_node.animate({"stroke-width": path_node.remanence}, 1000) });
	floats['path'+part1.name+part2.name] = path_node;
}
function disconnect_legs(elmt, involved) {
	var part1 = involved[0];
	var part2 = involved[1];
	if (part1 && part2) {
		var elmt = floats['path'+part1.name+part2.name];
		if (!elmt) {
			return;
		}
		//elmt.animate({opacity: 0.0, "stroke-width": 0.1}, 1000, function() {elmt.remove(); delete floats['path'+part1.name+part2.name]})
		elmt.animate({stroke: '#000', "stroke-width": elmt.remanence}, 1000);
		elmt.mouseover();
		elmt.mouseout();
		elmt.toBack();
		root_circle.toBack();
	}
}


/*************************************************
 * Effects
 */

function elmt_tooltip(elmt, x, y, text, r2) {
	var circle = elmt;
	var text_running=false;
	elmt.mouseover(function (event) {
		circle.animate({r:r2}, 1000, "elastic")
		if (!text_running) {
			if (circle.nick == circle.name) {
				text = circle.name + "/" + circle.state;
			}
			else {
				text = circle.nick + "/" + circle.name + "/" + circle.state;
			}
			if (circle.latency) {
				text += "/" + circle.latency
			}
			text_running=true;
			floats["text"+text] = paper.text(x+10, y, text)
						.attr({"font-size":16, fill: "#FFF"})
						.animate({fill: "#777", y:0, opacity: 0} ,5000, function() {text_running=false});
		}
		}) 
       .mouseout(function (event) {circle.animate({r:elmt.size}, 1000, "elastic")})
}

function dissapear(elmt) {
	var element = elmt;
	elmt.animate({fill: '#000'}, 100000, "<", function() { element.animate({opacity: 0.0}, 3000, function() { element.remove(); }) })
}

function hangup(elmt, to) {
	if (to == elmt.to) {
		elmt.animate({fill: "red"}, 1000, function() {dissapear(elmt)})
		if (to == "0")
			root_circle.animate({r: 60, fill: "#223fa3"}, 3000)
	}
}

function glowing_text(elmt, x, y, text, color) {
	var element = elmt;
	elmt.animate({stroke:'#FFF', 'stroke-width': 8, "stroke-opacity": 0.5},
		     1000,
		     function() {
			element.animate({stroke:'#000', 'stroke-width': 2, "stroke-opacity": 0.5},
					1000)
		     });
	floating_text(x, y, text, color)
}

function floating_pars(x, y, pars, call_id) {
	for (var i=0; i<pars.length; i++) {
		if (pars[i]) {
			calls[call_id+"text"+i] = paper.text(x-60+(Math.random() * 120), y-60+(Math.random() * 120), pars[i])
							.attr({"font-size":10, fill: "#FFF"})
							.animate({fill: "#777", y:0, opacity: 0} ,7000, function() { calls[call_id+"text"+i].remove();delete calls[call_id+"text"+i]; });
		}
	}
}


function floating_text(x, y, text, color, size, dest_y, cb) {
	if (!color)
		color = '#FFF'
	if (!size)
		size = 12;
	if (!dest_y)
		dest_y = 0;
	var elmt;
	if (cb)
		callback = function() { var idx = floats.indexOf(elmt); floats[idx].remove(); floats.splice(idx, 1); cb(); };
	else
		callback = function() { var idx = floats.indexOf(elmt); floats[idx].remove(); floats.splice(idx, 1); };
	elmt = paper.text(x, y, text).attr({"font-size":size, fill: color}).animate({fill: "#777", y:dest_y, opacity: 0} ,5000, callback);
	floats[floats.length] = elmt;
}


/*************************************************
 * Application logic
 */

function update_credit(credit, user_ext) {
	var credit_obj;
	console.log(credit)
	if (floats["credit"]) {
		if (user_ext == credit_obj.ext) {
			credit_obj = floats["credit"];
			credit_obj.attr({text: user_ext + " credit: "+credit})
			credit_diff = credit - credit_obj.credit
			credit_obj.credit = credit
			if (credit_diff) {
				if (credit_diff>0)
					credit_diff = "+" + credit_diff
				floating_text(60, 40, credit_diff, "#FFF", 20, 300)
			}
		} else {
			floating_text(60, 40, user_ext + " credit: "+credit, "#FFF", 20, 300)
		}
	}
	else {
		credit_obj = paper.text(60, 20, user_ext + " credit: "+credit).attr({"stroke":"#FFF", "font-size": 14})
		floats["credit"] = credit_obj
		credit_obj.credit = credit
		credit_obj.ext = user_ext
	}
}

function update_channel(elmt, x, y, pos_rad) {
	var color;
	// Set element color
	color = "hsb(" + pos_rad/(Math.PI*2.0) + ", .75, .8)";
	elmt.color = color

	if ($.inArray(elmt.new_state, UNAVAILABLE) != -1)
		color = '#000'
	if ($.inArray(elmt.state, UNAVAILABLE) != -1)
		color = '#000'
	

	if (!elmt.busy) {
		if (elmt.state) {
			elmt.animate({cx:x, cy:y, fill:color}, 1000);
		}
		else {
			elmt.attr({cx:x, cy:y, fill:color});
			elmt_tooltip(elmt, x+20, y, elmt.nick+"/"+elmt.name, r2=16)
		}
		elmt.x = x
		elmt.y = y
		if (elmt.new_state) {
			var text = elmt.nick;
			if (elmt.latency)
				text += " " + elmt.latency;
			floating_text(x, y, text, color)
			elmt.state = elmt.new_state
			elmt.new_state = false
		}
	}
}

function create_channel(channels, name, nick, latency, state, is_channel, size, pars) {
		if (!channels[name]) {
			// New channel
			if (is_channel || (state == 'OK' || state == 'LAGGED')) {
				channels[name] = paper.circle(200+(Object.keys(channels).length*20), 150, size)
				channels[name].new_state = state;
				channels[name].nick = nick;
				channels[name].name = name;
				channels[name].size = size;
				channels[name].latency = latency;
				channels[name].busy = false;
			}
		}
		else {
			// Channel already exists
			channel = channels[name];
			if (latency != channel.latency) {
				channel.latency = latency;
				if (latency)
					text = channel.nick + " " + latency;
				else
					text = channel.nick;
				glowing_text(channel, channel.x, channel.y, channel.nick, channel.color);
			}
			if (channel.state != state) {
				channel.new_state = state;
			}
		}
		if (!channels[name])
			return;

		if (channels[name].icon) {
			channels[name].icon.translate(1000,1000)
			channels[name].icon.remove()
			channels[name].icon = null
		}

		if (state == 'LAGGED') {
			channels[name].icon = paper.path(ICON_CLOUD).attr({fill: "#000", stroke: "#FFF"});
			channels[name].iconpos = [0,0]
		}
		if (pars && 'srtp' in pars) {
			if (channels[name].lockicon) {
				channels[name].lockicon.remove()
				channels[name].lockicon = null
			}
			if (pars['srtp']) {
				channels[name].lockicon = paper.path(ICON_LOCK).attr({fill: "#FFF", stroke: "#000"});
				channels[name].lockiconpos = [0,0]
			}
		}
}

function position_channels(channels, radius) {
	// Position objects in a circle and set other animations
	var keys = Object.keys(channels);
	for (var i=0; i<keys.length; i++) {
		var rad = (2.0*Math.PI)/keys.length;
		var pos_rad = rad*i;
		var x = 320 + radius*Math.cos(pos_rad)
		var y = 240 + radius*Math.sin(pos_rad)
		var key = keys[i];
		var elmt = channels[key];

		// Animate position and style
		update_channel(elmt, x, y, pos_rad);
		if (elmt.icon) {
			elmt.icon.translate(-elmt.iconpos[0], -elmt.iconpos[1])
			elmt.icon.translate(x-16, y-24)
			elmt.iconpos = [x-16, y-24]
		}
		if (elmt.lockicon) {
			elmt.lockicon.translate(-elmt.lockiconpos[0], -elmt.lockiconpos[1])
			elmt.lockicon.translate(x-16, y-24)
			elmt.lockiconpos = [x-16, y-24]
		}

	}
}

function create_channels(data_source, channels, radius, size, is_channel) {
	// Create new channels
	var keys = Object.keys(data_source);
	for (var i=0; i<keys.length; i++) {
		var key = keys[i];
		var name, nick, state, latency, channel;
		var data = data_source[key];
		if (is_channel) {
			nick = data['name'];
			state = data['status'];
			latency = data['ping'];
			ext = nick
		}
		else {
			ext = data['exten'];
			nick = data['name'];
			state = data['status'];
			latency = data['ping'];
		}
		create_channel(channels, ext, nick, latency, state, is_channel, size, data)
	}
	position_channels(channels, radius)
}

function create_call(call_id, x, y, text, from, to, pars) {
	var text_running = true;
	var call = paper.circle(x, y, 10+Math.random())
			.animate({fill: "#223fa3", stroke: "#000", "stroke-width": 5, "stroke-opacity": 0.5}, 2000)
			.mouseover(function (event) {
				call.animate({r:20}, 1000, "elastic")
				if (!text_running) {
					text_running=true;
					floating_text(x+10, y, text, '#FFF', 16, 0, function() {text_running=false});
					floating_pars(x, y, pars, call_id);
				}
				}) 
		       .mouseout(function (event) {call.animate({r:10}, 1000, "elastic")})
	call.from = from;
	call.to = to;
	call.legs = {};
	// first time so show popup text
	floating_text(x+10, y, text, '#FFF', 16, 0, function() {text_running=false});
	return call;
}

function check_legs(channel_data, from, to, call) {
	var channel;
	if (channel_data[from]) {
		channel = channel_data[from];
		call.legs[from] = channel;
	}
	else if (channel_data[to]) {
		channel = channel_data[to];
		call.legs[to] = channel;
	}
}

function parse_call(pars) {
	var call_id = pars['linkedid'];
	var call;
	var action = pars['eventname'];
	var from = pars['calleridnum'];
	var to = pars['exten'];
	console.log(from+" "+to)

	if (calls[call_id])  {
		call = calls[call_id]
	}
	else {
		// Create a new call
		var x = 270+(Math.random()*100);
		var y = 190+(Math.random()*100);
		var text = from + " to " + to;
		call = create_call(call_id, x, y, text, from, to, pars);
		calls[call_id] = call;
	}

	// Check conversation legs
	check_legs(all_channels['local'], from, to, call);
	check_legs(all_channels['channels'], from, to, call);

	// Calculate involved channels
	var involved = Array();
	var keys = Object.keys(call.legs);
	for(var i=0; i<keys.length; i++) {
		involved[involved.length] = call.legs[keys[i]];
	}
	console.log(involved)
	// Check call state
	switch (action) {
	    case "ANSWER":
		call.animate({fill: "green"}, 1000)
		// Activate all leg endpoints
		for(var i=0; i<involved.length; i++) {
			var channel = involved[i];
			channel.animate({fill: "#22a32f", stroke: "#000", "stroke-width": 5, "stroke-opacity": 0.5}, 2000, "backOut");
			channel.busy = true
		}
		break;
	    case "HANGUP":
		hangup(call, to)
		break;
	    case "CHAN_END":
		hangup(call, to)
		if (involved.length && to == call.to) {
			// Deactivate all leg endpoints
			for(var i=0; i<involved.length; i++) {
				var channel = involved[i];
				channel.animate({fill: channel.color, stroke: "#000", "stroke-width": 5, "stroke-opacity": 0.5}, 2000, "backOut");
				channel.busy = false
			}
			disconnect_legs(call, involved)
		}
		break;
	    case "CHAN_START":
		// Special animation for admin calls
		if (to == "0")
			root_circle.animate({r: 100, fill: "#FFF"}, 3000)
		// Colour all channel leg endpoints
		for(var i=0; i<involved.length; i++) {
			var channel = involved[i];
			channel.size += 0.1;
			channel.animate({r: channel.size, fill: "#FFF", stroke: "#000", "stroke-width": 5, "stroke-opacity": 0.5}, 2000, "backOut");
			channel.busy = true
		}
		// Connect legs
		if (involved.length > 1) {
			connect_legs(call, involved)
		}
		break;
	}
}


/*************************************************
 * Register events once document is ready
 */

$(document).ready( function () {
	paper = Raphael("canvas", 640, 480),
	root_circle = paper.circle(320, 240, 60).animate({fill: "#223fa3", stroke: "#000", "stroke-width": 80, "stroke-opacity": 0.5}, 2000, "backOut");

	if (!!window.EventSource) {
	  var source = new EventSource('/sse');
	} else {
	  // Result to xhr polling :(
	}
	source.addEventListener('message', function(e) {
		write_div(e.data, '#bla')
	}, false);

	source.addEventListener('callmonitor', function(e) {
		write_div(e.data, '#default')
	}, false);
	source.addEventListener('credit', function(e) {
		console.log(e.data);
		var data = JSON.parse(e.data);
		update_credit(data.credit, data.user)
	}, false);

	source.addEventListener('peers', function(e) {
		var data = JSON.parse(e.data);
		create_channels(data['local'], all_channels['local'], 90.0, 8, false);
		create_channels(data['channels'], all_channels['channels'], 150.0, 12, true);
	}, false);

	source.addEventListener('peer', function(e) {
		var peer_event = JSON.parse(e.data);
		//  {'peerstatus': 'Registered', 'peer': 'SIP/caedes', 'address': '109.69.14.162:42413', 'privilege': 'system,all', 'channeltype': 'SIP', 'event': 'PeerStatus'}
		// create_channel(channels, name, nick, latency, state, is_channel, size)
		var name = peer_event['exten']
		var nick = peer_event['username']
		var latency = null
		var status = null
		if (peer_event['channel'])
			section = 'channels'
		else
			section = 'local'
		if (peer_event['peerstatus'] == 'Registered' || peer_event['peerstatus'] == 'Reachable')
			status = 'OK'
		else if (peer_event['peerstatus'] == 'Lagged')
			status = 'LAGGED'
		else
			status = 'UNREACHABLE'
		console.log(peer_event)
		create_channel(all_channels['local'], name, nick, latency, status, peer_event['channel'], 8, peer_event);
		position_channels(all_channels['local'], 90.0);
	}, false);


	source.addEventListener('rtcheckcalls', function(e) {
		console.log(e.data);
		write_div(e.data, '#rtcheckcalls');
		var data = JSON.parse(e.data);
		parse_call(data)
	}, false);

	source.addEventListener('open', function(e) {
		write_div('connection started', '#default')
	}, false);

	source.addEventListener('channels', function(e) {
		write_div(e.data, '#default')
		var data = JSON.parse(e.data);
		if (root_text.length) {
			for (var i=0;i<root_text.length;i++) {
		//		delete root_text[i];
				channel = root_text[i]
				channel.animate({opacity:0.0}, 1000)
			}
			root_text = Array();
		}
		var text = "";
		for (var i=0;i<data.length;i++) {
			channel = data[i];
			text += channel['name']+" "+channel['format']+"\nrx: "+JSON.stringify(channel['rx'])+"\ntx: "+JSON.stringify(channel['tx'])+"\n";
		}
		var text1 = paper.text(250, 200, text)
				.attr({align:'left', fill:'#FFF'})
				.animate({fill:'#EEE'}, 6000, function() {text1.remove()})
		root_text[root_text.length] = text1;

	}, false);

	source.addEventListener('error', function(e) {
	  if (e.readyState == EventSource.CLOSED) {
	        // Connection was closed.
		write_div('connection closed', '#default')
	  }
	}, false);
} ); // document.load

