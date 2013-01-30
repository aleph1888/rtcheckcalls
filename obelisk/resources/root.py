from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.util import redirectTo

from obelisk.resources.peers import PeersResource
from obelisk.resources.user import UserResource
from obelisk.resources.prices import PricesResource
from obelisk.resources.login import LoginResource
from obelisk.resources.stats import StatsResource
from obelisk.resources.logout import LogoutResource
from obelisk.resources.providers import ProvidersResource
from obelisk.resources.calls import CallsResource
from obelisk.resources.sse import SSEResource
from obelisk.resources.credit import CreditResource
from obelisk.resources.register import RegisterResource
from obelisk.resources.options import OptionsResource
from obelisk.resources.changepass import ChangePassResource
from obelisk.templates import print_template
from obelisk.pricechecker import get_winners

from obelisk.testchannels import TestChannels
from obelisk.resources import sse

from obelisk import session

class RootResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("voip", PeersResource())
        self.putChild("prices", PricesResource())
        self.putChild("user", UserResource())
        self.putChild("sse", SSEResource())
        self.putChild("calls", CallsResource())
        self.putChild("password", ChangePassResource())
        self.putChild("credit", CreditResource())
        self.putChild("register", RegisterResource())
        self.putChild("options", OptionsResource())
        self.putChild("stats", StatsResource())
        self.putChild("providers", ProvidersResource())
        self.putChild("login", LoginResource())
        self.putChild("logout", LogoutResource())
        self.putChild("icons", File("/usr/share/icons"))
        self.putChild("tpl", File("/home/caedes/rtcheckcalls/templates"))
        self.putChild("sip", File("/home/lluis/tst_sip_gui"))
        self.putChild("jssip", File("/home/caedes/jssip"))
	reactor.callLater(1, self.get_winners)
	reactor.callLater(1, self.get_channel_test)
	self.channel_tester = TestChannels()

    def get_winners(self):
	get_winners()
	reactor.callLater(600, self.get_winners)

    def get_channel_test(self):
	reactor.callLater(5, self.get_channel_test)
	test = self.channel_tester.get_rates()
	if test:
		sse.resource.notify(test, 'channels', 'all')

    def getChild(self, name, request):
        return self

    def render_GET(self, request):

	output = "<li><a href='/prices'>precios</a></li>"

	user = session.get_user(request)
	if user:
		user_ext = user.voip_id
		output_user = "<li><a href='/user/"+user.voip_id+"'>datos usuario</a></li>"
		output_user += "<li><a href='/voip'>extensiones</a></li>"
		output_user += "<li><a href='/stats'>estadisticas</a></li>"
		if user.admin == 1:
			output_user += "<li><a href='/user/accounts'>credito total</a></li>"
			output_user += "<li><a href='/providers'>precios proveedores</a></li>"
			output_user += "<li><a href='/calls'>llamadas</a></li>"
			user_ext += " eres admin"
		output_user += "<li><a href='/logout'>logout</a></li>"

	        return print_template('logged-pbx-lorea', {'LINKS':output, 'LOGGED_LINKS':output_user, 'user': user_ext})
	else:
		output += "<li><a href='/register'>registrarse</a></li>"
	        return print_template('home-pbx-lorea', {'LINKS':output})

    def render_POST(self, request):
	return "<p>xxxxx</p>"
        #return redirectTo("pylibrarian.py", request)

