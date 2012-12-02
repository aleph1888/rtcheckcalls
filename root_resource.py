from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.util import redirectTo

from voipresource import VoipResource
from accountsresource import AccountResource
from pricesresource import PricesResource

class RootResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("voip", VoipResource())
        self.putChild("prices", PricesResource())
        self.putChild("user", AccountResource())
        self.putChild("icons", File("/usr/share/icons"))

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
	output = "<h1>Voip Daemon</h1>"
	output += "<p><a href='/voip'>extensiones</a></p>"
	output += "<p><a href='/prices'>precios</a></p>"
	output = "<html><body>%s</body></html>" % (output,)
        return output
        #return redirectTo("voip", request)

    def render_POST(self, request):
	return "<p>xxxxx</p>"
        #return redirectTo("pylibrarian.py", request)

