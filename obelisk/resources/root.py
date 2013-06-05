import os

from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.util import redirectTo, Redirect

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
from obelisk.resources.docs import DocsResource
from obelisk.resources.voicemail import VoiceMailResource
from obelisk.resources.admin import AdminResource
from obelisk.resources.tinc import TincResource
from obelisk.resources.dundi import DundiResource
from obelisk.resources.pln import PLNResource
from obelisk.resources.btcin import BtcInResource
from obelisk.templates import print_template
from obelisk.pricechecker import get_winners

from obelisk.rtcheckcalls import CallManager
from obelisk.asterisk import ami

from obelisk.testchannels import TestChannels
from obelisk.resources import sse
from obelisk.tools import ticker

from obelisk import session

from obelisk.resources.rooms import RoomsResource
from obelisk.resources.roomscategory import RoomsCategoryResource

import obelisk

class RootResource(Resource):
    def __init__(self):
        Resource.__init__(self)
	ami.connect()
	self.call_manager = CallManager()
	our_dir = os.path.dirname(os.path.dirname(obelisk.__file__))
	ami.connector.registerEvent('CEL', self.call_manager.on_event)
        self.putChild("voip", PeersResource())
        self.putChild("prices", PricesResource())
        self.putChild("voicemail", VoiceMailResource())
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
        self.putChild("admin", AdminResource())
        self.putChild("docs", DocsResource())
        self.putChild("icons", File("/usr/share/icons"))
        self.putChild("tpl", File(os.path.join(our_dir, "templates")))
        self.putChild("sip", File("/home/lluis/tst_sip_gui"))
        self.putChild("jssip", File("/home/caedes/jssip"))
        self.putChild("favicon.ico", File(os.path.join(our_dir, "templates", "telephone_icon.ico")))
        self.putChild("tinc", TincResource())
        self.putChild("dundi", DundiResource())
        self.putChild("pln", PLNResource())
        self.putChild("btcin", BtcInResource())
	self.putChild("rooms", RoomsResource())
	self.putChild("roomscategory", RoomsCategoryResource())
	if 'pln' in obelisk.config.config:
		pln_name = obelisk.config.config['pln']['name']
		self.putChild(pln_name, Redirect('/tinc/pubkey'))
		self.putChild(pln_name +'.pub', Redirect('/dundi/pubkey'))
	self.putChild('node.json', Redirect('/pln/node.json'))

	reactor.callLater(2, reactor.callInThread, self.get_winners)
	reactor.callLater(4, reactor.callInThread, self.get_channel_test)
	self.channel_tester = TestChannels()
        # start running the ticker
        ticker.ticker()

    def get_winners(self):
	get_winners()
	reactor.callLater(600, reactor.callInThread, self.get_winners)

    def get_channel_test(self):
	test = self.channel_tester.get_rates()
	if test:
		reactor.callFromThread(sse.resource.notify, test, 'channels', 'all')
	reactor.callLater(5, reactor.callInThread, self.get_channel_test)

    def getChild(self, name, request):
        return self

    def render_GET(self, request):

	output = "<li><a href='/prices'>precios</a></li>"
	output += "<li><a href='/docs'>documentacion</a></li>"

	user = session.get_user(request)
        main_page = print_template('portada', {})
	if user:
		user_ext = user.voip_id
		output_user = "<li><a href='/user/"+user.voip_id+"'>datos usuario</a></li>"
		output_user += "<li><a href='/voip'>listin telefonico</a></li>"
		output_user += "<li><a href='/stats'>estadisticas</a></li>"
		if user.admin == 1:
			output_user += "<li><a href='/admin'>admin</a></li>"
			user_ext += " eres admin"
		output_user += "<li><a href='/logout'>logout</a></li>"

	        return print_template('logged-pbx-lorea', {'LINKS':output, 'LOGGED_LINKS':output_user, 'user': user_ext, 'content': main_page})
	else:
		output += "<li><a href='/register'>registrarse</a></li>"
	        return print_template('home-pbx-lorea', {'LINKS':output, 'content': main_page})

    def render_POST(self, request):
	return "<p>xxxxx</p>"
        #return redirectTo("pylibrarian.py", request)

