from twisted.web.resource import Resource
import subprocess
from datetime import datetime

from obelisk.asterisk.prefixes import list_prices_json
from obelisk.prices import check_prices
from obelisk.templates import print_template
from obelisk import session

class PricesResource(Resource):
    def render_GET(self, request):
	logged = session.get_user(request)
	parts = request.path.split("/")
	if len(parts) > 2 and logged and logged.admin:
		section = parts[2]
		if section == 'check':
			output = check_prices()
			return print_template('content-pbx-lorea', {'content': "<pre>"+output+"</pre>"})
	res = list_prices_json()
	check_link = ""
	if logged and logged.admin:
		check_link = "<p><a href='/prices/check'>Chequear precios</a></p>"
	return print_template('prices-pbx-lorea', {'links': check_link, 'prices': res, 'map': print_template('prices-map-pbx-lorea', {})})

    def getChild(self, name, request):
        return self
