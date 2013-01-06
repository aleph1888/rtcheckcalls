from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.util import redirectTo

from voipresource import VoipResource
from accountsresource import AccountResource
from pricesresource import PricesResource
from loginresource import LoginResource
from logoutresource import LogoutResource
from templates import print_template

import session

class RootResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("voip", VoipResource())
        self.putChild("prices", PricesResource())
        self.putChild("user", AccountResource())
        self.putChild("login", LoginResource())
        self.putChild("logout", LogoutResource())
        self.putChild("icons", File("/usr/share/icons"))
        self.putChild("tpl", File("/home/caedes/rtcheckcalls/templates"))
        self.putChild("sip", File("/home/lluis/tst_sip_gui"))
        self.putChild("jssip", File("/home/caedes/jssip"))

    def getChild(self, name, request):
        return self

    def render_GET(self, request):

	output = "<li><a href='/prices'>precios</a></li>"

	user = session.get_user(request)
	if user:
		user_ext = user.voip_id
		output_user = "<li><a href='/user/"+user.voip_id+"'>datos usuario</a></li>"
		output_user += "<li><a href='/voip'>extensiones</a></li>"
		if user.admin == 1:
			output_user += "<li><a href='/user/stats'>estadisticas</a></li>"
			output_user += "<li><a href='/user/accounts'>credito total</a></li>"
			user_ext += " eres admin"
		output_user += "<li><a href='/logout'>logout</a></li>"

	        return print_template('logged-pbx-lorea', {'LINKS':output, 'LOGGED_LINKS':output_user, 'user': user_ext})
	else:
	        return print_template('home-pbx-lorea', {'LINKS':output})

    def render_POST(self, request):
	return "<p>xxxxx</p>"
        #return redirectTo("pylibrarian.py", request)

