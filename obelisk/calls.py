import time
from decimal import Decimal
from datetime import datetime

from obelisk.model import Model, Call, User, Provider

def get_calls(user_ext, logged, limit=0, offset=0, format='html'):
	model = Model()
	user = model.get_user_fromext(user_ext)
	if not user:
		return ""

	if format == 'html':
		res = ""
	else:
		res = []
	all_calls = user.calls
	last = len(all_calls)
	if limit and len(user.calls) > limit + offset:
		all_calls = user.calls[last-offset-limit:last-offset]
	for call in all_calls:
		destination = call.destination
		date = call.timestamp
		duration = call.duration
		duration = "%sm %ss" % (duration/60, duration%60)
		cost = call.cost
		rate = call.rate
		if call.provider:
			provider = call.provider.name
		else:
			provider = 'unknown'
		pars = [date, destination, duration, cost, rate]
		if logged and logged.admin:
			pars.append(provider)
			if format == 'html':
				res = ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%.3f</td><td>%.3f</td><td>%s</td></tr>\n" % tuple(pars)) + res
		else:
			if format == 'html':
				res = ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%.3f</td><td>%.3f</td></tr>\n" % tuple(pars)) + res
		if format == 'json':
			pars[0] = str(pars[0])
			pars[3] = float(pars[3])
			pars[4] = float(pars[4])
			res = [pars] + res
	return res

def add_call(user_ext, destination, date, real_duration, duration, cost, rate, provider_name):
	model = Model()
	user = model.get_user_fromext(user_ext)
	provider = model.query(Provider).filter_by(name=provider_name).first()
	if not provider:
		provider = Provider(provider_name)
		model.session.add(provider)
		model.session.commit()
	call = Call(user=user,
			destination=destination,
			timestamp=datetime.fromtimestamp(float(date)),
			duration=real_duration,
			charged=duration,
			cost=cost,
			rate=rate,
			provider=provider)

	model.session.add(call)
	model.session.commit()

if __name__ == "__main__":
	print get_calls("816")
	add_call('816', '666', time.time(), 666, 720, '0.42', 0.0023, 'blah')
	print get_calls("816")
	print get_calls("728")
