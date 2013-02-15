import os

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import session
from obelisk.templates import print_template
from obelisk.asterisk import cli
from obelisk.asterisk.dundi import Dundi
from obelisk.tools import html
from ping import do_one

import obelisk

class DundiResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        #self.putChild("voip", PeersResource())

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
	user = session.get_user(request)
	if user and user.admin:
		content = self.render_dundi(request)
	        #content = print_template('admin', {})
	        return print_template('content-pbx-lorea', {'content': content})
	else:
		return redirectTo("/", request)

    def render_dundi(self, request):
	d = Dundi()
	output = "<h2>Dundi</h2>\n"
	output += "<h3>Server</h3>\n"
	output += "<p><b>geo</b>: %s <b>nongeo</b>: %s</p>\n" % (str(d.geo), str(d.nongeo))
	for key in ['locality', 'organization', 'entityid', 'email']:
		val = d.config['general'][key]
		output += '<p><b>%s:</b> %s</p>\n' % (key, val)
	output += "<h3>Peers</h3>\n"
	output += self.render_dundipeers(request, d.find_hosts())
	return output

    def render_dundipeers(self, request, peers):
	res = [['name', 'address', 'nongeo', 'alias', 'online']]
	for name, node in peers.iteritems():
		address = node.get('host', '')
		nongeo = str(node.get('nongeo', ''))
		alias = str(node.get('inkey', ''))
		online = 'no'
		if address:
			ping = do_one(address, 1)
			if ping:
				online = 'si ' + str(int(ping*1000))
		res.append([name, address, nongeo, alias, online])
	return html.format_table(res)

