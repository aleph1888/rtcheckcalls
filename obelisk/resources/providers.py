from twisted.web.resource import Resource
from twisted.web.util import redirectTo

import pprint

from obelisk import pricechecker
from obelisk import templates

class ProvidersResource(Resource):
    def __init__(self):
	Resource.__init__(self)
    def render_GET(self, request):
	winners = '<pre>'+pprint.pformat(pricechecker.winners)+'</pre>'
	providers_html = ""
	for provider, provider_url in pricechecker.providers.iteritems():
		providers_html += "<a href='%s'>%s</a> " % (provider_url, provider)
        return templates.print_template('content-pbx-lorea', {'content': winners + '<h2>Providers checked: </h2>' + providers_html})

