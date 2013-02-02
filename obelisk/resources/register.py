from twisted.web.resource import Resource
from twisted.web.util import redirectTo
import re

from obelisk.accounting import accounting
from decimal import Decimal
from obelisk import session

from obelisk.model import Model
from obelisk.resources import login

from obelisk.templates import print_template

from obelisk.asterisk.users import create_user

class RegisterResource(Resource):
    def render_POST(self, request):
	args = {'user':'', 'password':'', 'email':''}
        for a in request.args:
            args[a] = request.args[a][0]

	if args['user'] and args['password']:
		user = args['user']
		password = args['password']
		if args['email']:
			email = args['email']
			if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
				args['email'] = ''
				args['error'] = 'error: email con formato incorrecto'
				return self.render_register(args)
		else:
			email = ''
		if user.isalnum() and len(user) < 50 and len(user) > 1:
			res = create_user(user, password)
			if res:
				return login.resource.login(user, password, request, email)
			else:
				args['error'] = 'error: nombre de usuario no disponible'
				return self.render_register(args)
		else:
			args['error'] = 'error: nombre de usuario con formato incorrecto'
			return self.render_register(args)
	args['error'] = 'error: debes introducir por lo menos usuario y contrasenya'
	return self.render_register(args)

    def render_register(self, args={'user':'', 'password':'', 'email':'', 'error': ''}):
	content = print_template('register', args)
	return print_template('content-pbx-lorea', {'content': content})
	#return "no registrations today, sorry"

    def render_GET(self, request):
	res = None
	logged = session.get_user(request)
	return self.render_register()

