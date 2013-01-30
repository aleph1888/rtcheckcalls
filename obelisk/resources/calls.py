from twisted.web.resource import Resource
from twisted.web.util import redirectTo

import pprint
import json
import time

from obelisk import pricechecker
from obelisk import session
from obelisk.templates import print_template
from obelisk.model import Model, Call, User

import datetime

colors = ['orange', '#FF3300', '#FFFF00', '#FF66CC', '#FF0099', '#99CCCC', '#FFFF99', 'blue', 'yellow', 'green', 'red']
providers_colors = {}

class CallsResource(Resource):
    def __init__(self):
	Resource.__init__(self)
    def format_date(self, dt):
	dt = time.strftime("%Y-%m-%d %H:%M:%SZ", dt.timetuple())
	return dt

    def get_provider_name(self, provider):
	if provider and provider.name and not provider.name == 'blah':
		name = provider.name
	else:
		name = 'unknown'
	return name

    def get_color(self, provider):
	name = self.get_provider_name(provider)
	if not name in providers_colors:
		n = len(providers_colors)
		providers_colors[name] = n
	return colors[providers_colors[name]]

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
	user = session.get_user(request)
	if not user or not user.admin:
		return redirectTo("/", request)
	try:
		parts = request.path.split("/")
	except:
		parts = ['','calls', 'all']
	if len(parts) > 2:
		if parts[2] == 'all':
			return self.render_all()
		else:
			return self.render_all(parts[2])
	else:
		return print_template('timeline', {})
    def render_all(self, user_ext=None):
	model = Model()
	result = {}
	result['dateTimeFormat'] = 'iso8601'
	result['wikiURL'] = 'http://simile.mit.edu/shelf/'
	result['wikiSection'] = 'Simile Cubism Timeline'
	result['events'] = []
	events = result['events']
	if user_ext:
		user = model.query(User).filter_by(voip_id=user).first()
		calls = model.query(Call).filter_by(user=user)
	else:
		calls = model.query(Call)
	for call in calls:
		if not call.user:
			print "call without user!", call
			continue
		event = {}
		event['start'] = self.format_date(call.timestamp)
		event['end'] = self.format_date(call.timestamp+datetime.timedelta(seconds=float(call.duration)))
		event['title'] = "from %s to %s" % (call.user.voip_id, call.destination)
		provider_name = self.get_provider_name(call.provider)
		event['description'] = "from %s to %s.<br/>duration: %.2fmin<br/>provider: %s" % (call.user.voip_id, call.destination, float(call.duration)/60.0, provider_name)
		event['color'] = self.get_color(call.provider)
	#	event['description'] = ""
#		event['image'] = ""
#		event['link'] = ""
		events.append(event)
        return json.dumps(result)

