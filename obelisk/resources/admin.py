import os

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import session
from obelisk.resources.tinc import TincResource
from obelisk.resources.dundi import DundiResource
from obelisk.templates import print_template

import obelisk

class AdminResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("tinc", TincResource())
        self.putChild("dundi", DundiResource())

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
	user = session.get_user(request)
	if user and user.admin:
	        content = print_template('admin', {})
	        return print_template('content-pbx-lorea', {'content': content})
	else:
		return redirectTo("/", request)

