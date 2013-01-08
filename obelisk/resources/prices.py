from twisted.web.resource import Resource
import subprocess
from datetime import datetime

from obelisk.prices import list_prices_json
from obelisk.templates import print_template

class PricesResource(Resource):
    def render_GET(self, request):
	res = list_prices_json()
	return print_template('prices-pbx-lorea', {'prices': res, 'map': print_template('prices-map-pbx-lorea', {})})

