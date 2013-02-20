import json
import os

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk.templates import print_template

from obelisk.asterisk.dundi import Dundi
from obelisk.asterisk.tinc import Tinc

class PLNResource(Resource):
    def __init__(self):
	Resource.__init__(self)
	self._dundi = Dundi()
	self._tinc = Tinc()

    def is_pln_request(self, request):
	# check to see if this is a pln request
	headers = request.getAllHeaders()
	if 'x-forwarded-for' in headers:
		client_ip = headers['x-forwarded-for']
	else:
		client_ip = request.getClientIP()
	if client_ip.startswith('1.'):
		return True
	return False

    def render_GET(self, request):
	pln_request = self.is_pln_request(request)

	parts = request.path.split('/')
	if pln_request and len(parts) > 2 and parts[2] == 'node.json':
		return self.render_node_json()

	return print_template('pln', {})

    def render_node_json(self):
	from obelisk.config import config
	url = config['url']
	name = config['pln']['name']
	tinc_publickey = os.path.join(url, name)
	dundi_publickey = os.path.join(url, name + '.pub')
	node = {'nodeShortName': self._tinc.name,
		'hostname': self._tinc.address,
		'vpn_ip': self._tinc.subnet,
		'dundi_publickey': dundi_publickey,
		'tinc_publickey': tinc_publickey,
		'admin_email': self._dundi.config['general']['email'],
		}
	if len(self._dundi.geo) > 1:
		node['geographic_phone_number'] = list(self._dundi.geo)
	else:
		node['geographic_phone_number'] = self._dundi.geo[0]
	if len(self._dundi.nongeo) > 1:
		node['non_geographic_phone_number'] = list(self._dundi.nongeo)
	else:
		node['non_geographic_phone_number'] = self._dundi.nongeo[0]
	return json.dumps(node)

    def getChild(self, name, request):
        return self

