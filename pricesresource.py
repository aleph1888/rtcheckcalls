from twisted.web.resource import Resource
from prices import list_prices
import subprocess
from datetime import datetime
from templates import print_template

class PricesResource(Resource):
    def render_GET(self, request):
	res = list_prices()
	return print_template('content-pbx-lorea', {'content': res})

