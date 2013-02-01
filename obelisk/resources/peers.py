import subprocess

from twisted.web.resource import Resource
from twisted.web.util import redirectTo
from twisted.internet import reactor

from obelisk import session
from obelisk.templates import print_template

from obelisk.resources import sse
from obelisk.asterisk import ami
from obelisk.model import Model
from obelisk.asterisk.model import SipPeer

resource = None

class PeersResource(Resource):
    def __init__(self):
	global resource
	Resource.__init__(self)
	resource = self
	self._peers = self.get_peers()
	ami.connector.registerEvent('PeerStatus', self.on_peer_event)
	reactor.callLater(10, self.get_peers_loop)
    def add_ip_href(self, line):
	ip_start = line.find("192.168.")
	ip_end = line.find(" ", ip_start)
	ip = line[ip_start:ip_end]
	return line.replace(ip, "<a href='http://"+ip+"'>"+ip+"</a>")
    def on_peer_event(self, event):
	peer_name = event['peer'].split('/')[1]
	model = Model()
	peer = model.query(SipPeer).filter_by(name=peer_name).first()
	if peer:
		event['username'] = peer_name
		event['exten'] = peer.regexten
		event['useragent'] = peer.useragent
		event['channel'] = False
		if peer.fullcontact and 'transport=TLS' in peer.fullcontact:
			event['tls'] = True
		else:
			event['tls'] = False
		if peer.encryption == 'yes':
			event['srtp'] = True
		else:
			event['srtp'] = False
		sse.resource.notify(event, 'peer' ,'all')
	else:
		sse.resource.notify(event, 'peer' ,'all')
		event['channel'] = True
    def get_extension(self, line, dialplan):
	try:
	    name = line.split(" ", 1)[0].split("/")[0]
	except:
	    return ""
	coded_name = "SIP/"+name+")"
	try:
	    dialplan_line = filter(lambda s: coded_name in s, dialplan)[0]
	except:
	    return ""
	ext_start = dialplan_line.find("'")
	return dialplan_line[ext_start+1: dialplan_line.find("'", ext_start+1)]
    def get_peers_loop(self):
	peers = self.get_peers()
	sse.resource.notify(peers, 'peers' ,'all')
	reactor.callLater(5, self.get_peers_loop)
    def get_peers(self):
	model = Model()
	output = self.run_asterisk_cmd('sip show peers')
	lines = output.split("\n")
	res = ""
	formatted = {"local": [],
		     "channels": [],
		     "end": []}
	for line in lines[1:]:
		line = line.replace(" D ", "")
		line = line.replace(" N ", "")
		line = line.replace(" a ", "")
		line = line.replace(" A ", "")
		line = line.replace("Cached RT", "")
		parts = line.split()
		parts = map(lambda s: s.strip("()"), parts)
		if len(parts) > 8 or len(parts) <= 3 :
			continue
		peer_name = parts[0].split("/")[0]
		ext = None
		port = parts[2].strip()
		peer = model.query(SipPeer).filter_by(name=peer_name).first()
		output = {'name': peer_name, 'status': parts[3]}
		if peer:
			ext = peer.regexten
		if ext: # and "192.168." in line:
			# line = self.add_ip_href(line)
			dest = 'local'
			output['useragent'] = peer.useragent
			if peer.encryption == 'yes':
				output['srtp'] = True
			else:
				output['srtp'] = False
			if peer.fullcontact and 'transport=TLS' in peer.fullcontact:
				output['tls'] = True
			else:
				output['tls'] = False
		else:
			dest = 'channels'
		if len(parts) > 4 and not port == '0':
			# connected
			if dest == 'channels':
				output['ping'] = parts[4]
			else:
				output['exten'] = ext
				output['ping'] = parts[4]
		elif len(parts) > 3:
			if ext:
				output['exten'] = ext
		formatted[dest].append(output)
	return formatted

    def render_GET(self, request):
	user = session.get_user(request)
	if not user:
		return redirectTo("/", request)
	model = Model()
	output = self.run_asterisk_cmd('sip show peers')
	lines = output.split("\n")
	res = ""
	formatted = {"local": "<tr><th>Nombre</th><th>Ext</th><th>Estado</th><th>Latencia</th><tr>\n",
		     "channels": "<tr><th>Nombre</th><th>Estado</th><th>Latencia</th><tr>\n",
		     "end": "<tr><th>Nombre</th><th>Ext</th><th>Estado</th><th>Latencia</th><tr>\n"}
	for line in lines[1:]:
		line = line.replace(" D ", "")
		line = line.replace(" N ", "")
		line = line.replace(" a ", "")
		line = line.replace(" A ", "")
		line = line.replace("Cached RT", "")
		parts = line.split()
		parts = map(lambda s: s.strip("()"), parts)
		if len(parts) > 8 or len(parts) <= 3 :
			continue
		peer_name = parts[0].split("/")[0]
		ext = None
		peer = model.query(SipPeer).filter_by(name=peer_name).first()
		if peer:
			ext = peer.regexten

		if ("OK" in line or "LAGGED" in line) and ext: # and "192.168." in line:
			# line = self.add_ip_href(line)
			dest = 'local'
		elif ext:
			dest = 'end'
		else:
			dest = 'channels'
		if len(parts) > 4:
			# connected
			if dest == 'channels':
				output = "<tr><td>%s</td><td>%s</td><td>%sms</td><tr>" % (peer_name, parts[3], parts[4])
			else:
				output = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%sms</td><tr>" % (peer_name, ext, parts[3], parts[4])
		elif len(parts) > 3:
			if dest == 'channels':
				output = "<tr><td>%s</td><td>%s</td><td></td>" % (peer_name, parts[3])
			else:
				output = "<tr><td>%s</td><td>%s</td><td>%s</td><td></td>" % (peer_name, ext, parts[3])
		else:
			print "not enough parts", parts
			continue
		formatted[dest] += output+"\n"
	res += "<h2>Local</h2>"
	res += "<table>"
	res += formatted['local']
	res += "</table>"
	if user.admin:
		res += "<h2>Channels</h2><table>"
		res += formatted['channels']
		res += "</table>"
	res += "<h2>Other</h2><table>"
	res += formatted['end']
	res += "</table><pre>"
	res += "<h2>Calls</h2>"
	res += self.run_asterisk_cmd('core show calls')
	res += "</pre><pre>"
	res += self.run_asterisk_cmd('core show uptime')
	res += "</pre>"
	return print_template('content-pbx-lorea', {'content': res})
    def run_asterisk_cmd(self, cmd):
	return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])
    def run_command(self, cmd):
 	output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	return output


