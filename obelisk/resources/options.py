from twisted.web.resource import Resource
from twisted.web.util import redirectTo
import subprocess

from obelisk.accounting import accounting
from decimal import Decimal
from obelisk import session

from obelisk.model import Model
from obelisk.resources import login

from obelisk.templates import print_template
from obelisk.asterisk.users import change_options, get_options
from obelisk.session import get_user

class OptionsResource(Resource):
    def render_POST(self, request):
	logged = get_user(request)
	if not logged:
		return redirectTo("/", request)
	args = {}
	options = {}
	user_ext = logged.voip_id
        for a in request.args:
            args[a] = request.args[a][0]

	if logged:
		if 'tls' in args and args['tls']:
			options['tls'] = args['tls']
		else:
			options['tls'] = False
		if 'srtp' in args and args['srtp']:
			options['srtp'] = args['srtp']
		else:
			options['srtp'] = False
		options['voicemail'] = args.get('voicemail', False)
		if 'ext' in args and args['ext'] and logged.admin:
			user_ext = args['ext']
		if 'lowquality' in args and args['lowquality']:
			options['codecs'] = ['gsm']
		change_options(user_ext, options)
		return redirectTo('/options/' + user_ext, request)
	return redirectTo('/', request)

    def render_GET(self, request):
	res = None
	logged = session.get_user(request)
	if not logged:
		return redirectTo('/', request)
	parts = request.path.split("/")
	if len(parts) > 2 and logged.admin:
		user_ext = parts[2]
	else:
		user_ext = logged.voip_id
	args = {'ext': user_ext, 'lowquality': '', 'tls': '', 'srtp': '', 'voicemail': ''}
	options = get_options(user_ext)
	if 'codecs' in options and 'gsm' in options['codecs']:
		args['lowquality'] = ' checked '
	if options['tls']:
		args['tls'] = ' checked '
	if options['srtp']:
		args['srtp'] = ' checked '
	if options['voicemail']:
		args['voicemail'] = ' checked '
	content = print_template('options', args)
	return print_template('content-pbx-lorea', {'content': content})

    def getChild(self, name, request):
        return self
