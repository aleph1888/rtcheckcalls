from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import templates
import obelisk.model
from datetime import datetime
import time
from sqlalchemy import and_
from obelisk.tools import html
from obelisk import session

class ProvidersResource(Resource):
    def __init__(self):
	Resource.__init__(self)
    def render_GET(self, request):
	logged = session.get_user(request)
	if logged and logged.admin:
		content = self.render_stats(request)
		content = "<pre>%s</pre>" % (content,)
		return templates.print_template('content-pbx-lorea', {'content': content})
	return redirectTo("/", request)
    def render_stats(self, request):
	output = "<h2>Estadisticas llamadas en el ultimo mes</h2>"
	model = obelisk.model.Model()
	ts_start = time.time() - 60*60*24*30
	calls = model.query(obelisk.model.Call).filter(obelisk.model.Call.timestamp>datetime.fromtimestamp(ts_start))
	all_calls = set()
	es_mobiles = set()
	mobiles_min = 0.0
	mobiles_min_2 = 0.0
	mobiles_min_3 = 0.0
	mobiles_min_4 = 0.0
	es_fixes = set()
	users = set()
	mobile_freq = {}
	for c in calls:
		if c.user:
			users.add(c.user.voip_id)
		destination = c.destination
		destination = destination.replace('+', '00')
		if len(destination) == 3:
			continue
		elif destination.startswith('0000'):
			continue
		elif len(destination) == 9:
			destination = '0034' + destination
		if destination.startswith('00349') or destination.startswith('00348'):
			es_fixes.add(destination)
		elif destination.startswith('0034'):
			es_mobiles.add(destination)
			mobiles_min += c.charged/60.0
			if destination in mobile_freq:
				mobile_freq[destination] += 1
			else:
				mobile_freq[destination] = 1
		all_calls.add(destination)

	# call stats for last month
	output += 'total calls %d\n' % (len(all_calls),)
	output += 'distinct es fix ' + str(len(es_fixes)) + "\n"
	output += 'distinct es mob %d \n' % (len(es_mobiles),)
	output += 'distinct users: %d minutes to mobiles: %d\n' % (len(users), mobiles_min)
	mobile_freq_2 = filter(lambda s: mobile_freq[s] > 1, mobile_freq)
	mobile_freq_3 = filter(lambda s: mobile_freq[s] > 2, mobile_freq_2)
	mobile_freq_4 = filter(lambda s: mobile_freq[s] > 3, mobile_freq_3)

	for c in calls:
		destination = c.destination
                destination = destination.replace('+', '00')
		if len(destination) == 9:
			destination = '0034' + destination
		if destination in mobile_freq_2:
			mobiles_min_2 += c.charged/60.0
		if destination in mobile_freq_3:
			mobiles_min_3 += c.charged/60.0
		if destination in mobile_freq_4:
			mobiles_min_4 += c.charged/60.0


	output += "frequencies: 2/%d/%d 3/%d/%d 4/%d/%d\n" % (len(mobile_freq_2), mobiles_min_2, len(mobile_freq_3), mobiles_min_3, len(mobile_freq_4), mobiles_min_4)

	# call stats per provider
	output += "<h2>Llamadas por proveedor en la ultima semana</h2>"
	ts_start_week = time.time() - 60*60*24*7
	providers = model.query(obelisk.model.Provider)
	results = []
	for provider in providers:
		if not provider.name:
			continue
		calls = provider.calls.filter(obelisk.model.Call.timestamp>datetime.fromtimestamp(ts_start_week))
		total_time = 0
		total_calls = 0
		total_freq_2 = 0
		total_freq_3 = 0
		total_freq_4 = 0
		for call in calls:
			duration = call.charged
			if call.rate == 0.0:
				total_time += duration/60.0
				total_calls += 1
			destination = call.destination.replace('+', '00')
			if len(destination) == 9:
				destination = '0034' + destination
			if destination in mobile_freq_2:
				total_freq_2 += duration / 60.0
			if destination in mobile_freq_3:
				total_freq_3 += duration / 60.0
			if destination in mobile_freq_4:
				total_freq_4 += duration / 60.0


		results.append([provider.name, "%d" % (total_time,), str(total_calls), str(len(list(calls))), str(total_freq_2), str(total_freq_3), str(total_freq_4)])
	output += html.format_table([["Nombre", "Minutos gratis", "Llamadas gratis", "Total llamadas", "Freq 2", "Freq 3", "Freq 4"]]+results)
	return output

