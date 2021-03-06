import os

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import session
from obelisk.templates import print_template
from obelisk.asterisk import cli
from obelisk.asterisk.tinc import Tinc
from obelisk.tools import html
from obelisk.tools.htmltool import ok_icon, format_ping
from ping import do_one

import obelisk

class TincResource(Resource):
    def __init__(self):
        Resource.__init__(self)
	self.tinc = Tinc()
        #self.putChild("voip", PeersResource())

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
	parts = request.path.split('/')
	if len(parts) > 2 and parts[2] == 'pubkey':
		return self.tinc.get_public_key()
	user = session.get_user(request)
	if user and user.admin:
		content = self.render_tinc(request)
	        #content = print_template('admin', {})
	        return print_template('content-pbx-lorea', {'content': content})
	else:
		return redirectTo("/", request)

    def render_tinc(self, request):
	t = Tinc()
	output = '<h2>Tinc</h2>\n'
	output += '<h3>Server</h3>\n'
	output += '<p>name: %s ip: %s address: %s</p>\n' % (t.name, t.subnet, t.address)
	output += '<h3>Peers</h3>\n'
	output += self.render_tincpeers(request, t)
	return output

    def render_tincpeers(self, request, tinc):
	res = [['name', 'address', 'subnet', 'signal']]
	for name, node in tinc.nodes.iteritems():
		address = node.get('address', '')
		subnet = node.get('subnet', '')
		online = ok_icon(False)
		if subnet:
			ping = do_one(subnet, 1)
			if ping:
				online = format_ping(ping)
			else:
				online = format_ping(False)
		res.append([name, address, subnet, online])
	return html.format_table(res)

