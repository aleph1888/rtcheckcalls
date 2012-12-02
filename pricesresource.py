from twisted.web.resource import Resource
from prices import list_prices
import subprocess
from datetime import datetime
import csv

class PricesResource(Resource):
    def render_GET(self, request):
	res = list_prices()
        return "<html><body>%s</body></html>" % (res,)

