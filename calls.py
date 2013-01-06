import time
from model import Model, Call, User
from decimal import Decimal
from datetime import datetime

def get_calls(user_ext):
	model = Model()
	user = model.get_user_fromext(user_ext)
	if not user:
		return ""

	res = ""
	for call in user.calls:
		destination = call.destination
		date = call.timestamp
		duration = call.duration
		duration = "%sm %ss" % (duration/60, duration%60)
		cost = call.cost
		rate = call.rate
		res = ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%.3f</td><td>%.3f</td></tr>\n" % (date, destination, duration, cost, rate)) + res

	return res

def add_call(user_ext, destination, date, real_duration, duration, cost, rate):
	model = Model()
	user = model.get_user_fromext(user_ext)
	call = Call(user=user,
			destination=destination,
			timestamp=datetime.fromtimestamp(float(date)),
			duration=real_duration,
			charged=duration,
			cost=cost,
			rate=rate)

	model.session.add(call)
	model.session.commit()

def get_stats():
	res = ""
	total = 0
	total_free = 0
	free_calls = 0
	cost_calls = 0
	total_cost = Decimal()
	total_benefit = Decimal()
	model = Model()
	calls = model.query(Call)
	for call in calls:
		cost = Decimal(call.cost)
		duration = call.charged
		minutes = duration/60
		if cost:
			total += duration
			cost_calls += 1
			total_cost += cost
			total_benefit += Decimal(minutes)*Decimal(0.001) + Decimal(0.001)
		else:
			total_free += duration
			free_calls += 1
	res += "<p>priced minutes %s</p>\n" % (total/60,)
	res += "<p>free minutes %s</p>\n" % (total_free/60,)
	res += "<p>calls %s free %s cost %s</p>\n" % (calls.count(), free_calls, cost_calls)
	res += "<p>cost %.3f benefit %.3f</p>\n" % (total_cost, total_benefit)
	return res

if __name__ == "__main__":
	print get_stats()
	print get_calls("816")
	add_call('816', '666', time.time(), 666, 720, '0.42', 0.0023)
	print get_calls("816")
	print get_calls("728")
