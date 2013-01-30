from twisted.web.resource import Resource
from twisted.web.util import redirectTo
import subprocess
from datetime import datetime
import csv

from obelisk.accounting import accounting
from obelisk.asterisk.users import parse_users
from decimal import Decimal
from obelisk import charges
from obelisk import calls
from obelisk import session

from obelisk.model import Model

from obelisk.templates import print_template

class UserResource(Resource):
    def __init__(self):
	print "INIT ACCOUNT RESOURCE"
	Resource.__init__(self)
	self._accounting = accounting
    def add_ip_href(self, line):
	ip_start = line.find("192.168.")
	ip_end = line.find(" ", ip_start)
	ip = line[ip_start:ip_end]
	return line.replace(ip, "<a href='http://"+ip+"'>"+ip+"</a>")
    def get_extension(self, line, dialplan):
	try:
	    name = line.split(" ", 1)[0].split("/")[1]
	except:
	    return ""
	coded_name = "SIP/"+name+")"
	try:
	    dialplan_line = filter(lambda s: coded_name in s, dialplan)[0]
	except:
	    return ""
	ext_start = dialplan_line.find("'")
	return dialplan_line[ext_start+1: dialplan_line.find("'", ext_start+1)]

    def render_GET(self, request):
        args = {}
        for a in request.args:
            args[a] = request.args[a][0]

	logged = session.get_user(request)
	if 'account' in args:
		res = args['account']
	else:
		parts = request.path.split("/")
		if len(parts) > 2:
			user = parts[2]
			if user == 'accounts':
				res = self.render_accounts(request)
			elif logged and (logged.voip_id == user or logged.admin == 1):
				res = self.render_user(user, request)
				return res
			else:
				return redirectTo("/", request)
	if isinstance(res, str):
		return print_template('content-pbx-lorea', {'content': res})
	else:
		return res

    def render_accounts(self, request):
	res = "<h2>accounts</h2>"
	logged = session.get_user(request)
	if not logged or not logged.admin:
		return redirectTo("/", request)
	data = self._accounting.get_data()
	total_credit = Decimal()
	users, _ = parse_users("/etc/asterisk/sip.conf")
	for ext, credit in data.items():
		username = "unknown"
		if ext in users:
			username = users[ext]
		res += "<p>%s <a href='/user/%s'>%s</a> %.3f</p>" % (str(ext), str(ext), str(username), credit)
		total_credit += Decimal(credit)
	res += "<p>total credit: %s</p>" % (total_credit,)
	return res

    def render_user(self, user_ext, request):
	model = Model()
	users, _ = parse_users("/etc/asterisk/sip.conf")
	creditlink = ''
	if user_ext in users:
		username = users[user_ext]
	else:
		username = user_ext
	user = model.get_user_fromext(user_ext)
	logged = session.get_user(request)
	if user:
		credit = "%.3f" % (user.credit,)
		user_charges = charges.get_charges(user_ext)
		user_calls = calls.get_calls(user_ext, logged)
		creditlink = ""
		if user.credit > 0:
			if user.voip_id == logged.voip_id:
				creditlink += '<a href="/credit/transfer">Transferir</a>'
			else:
				creditlink += '<a href="/credit/transfer/%s">Transferir</a>' % (user.voip_id)
		if logged.admin:
			creditlink += ' <a href="/credit/add/%s">Crear</a>' % (user.voip_id)
	else:
		credit = 0.0
		user_charges = ""
		user_calls = ""
	all_calls = self.render_user_calls(user_ext, request)
	args = {'ext': user_ext, 'username': username, 'credit': credit, 'credit_link':creditlink ,'calls': user_calls, 'charges': user_charges, 'all_calls': all_calls}
	return print_template('user-pbx-lorea', args)
    def render_user_calls(self, user_ext, request):
	FILE = "/var/log/asterisk/cdr-csv/Master.csv"
	f = open(FILE)
	csv_file = csv.reader(f)
	data = list(csv_file)
	logged = session.get_user(request)
	res = ""
	calls = ""
	for a in data:
		time_1 = a[9]
		time_2 = a[10]
		time_3 = a[11]
		duration = a[12]
		billsecs = int(a[13])
		from_ext = a[1]
		from_name = a[4]
		status = a[-4]
		id = a[-2]
		delta = 0.0
		#totalsecs += int(billsecs)
		t1 = datetime.strptime(time_1, "%Y-%m-%d %H:%M:%S")
		to_ext = a[2]
		if time_3:
			t2 = datetime.strptime(time_3, "%Y-%m-%d %H:%M:%S")
			delta = t2-t1
		if from_ext == user_ext or to_ext == user_ext:
			#calls = "<p>[%s] %s to %s for %s secs on %s/%s/%s %s</p>" % (id, from_ext, to_ext, delta, t1.day, t1.month, t1.year, status) + calls
			date = "%s/%s/%s" % (t1.day, t1.month, t1.year)
			if not from_ext == user_ext and logged.admin:
				from_ext = "<a href='/user/%s'>%s</a>" % (from_ext, from_ext)
			if not to_ext == user_ext and logged.admin:
				to_ext = "<a href='/user/%s'>%s</a>" % (to_ext, to_ext)
			calls = ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (date, from_ext, to_ext, delta, status)) + calls

		#if status == "ANSWERED" and (billsecs > umbra or not umbra):
		#	print from_ext,"->"," "*(14-len(a[2]))+a[2]+" ["+str(billsecs)+"]\t"+str(t1.day)+"\t"+str(t1.hour)
	res += calls
	return res
    def getChild(self, name, request):
        return self
    def run_asterisk_cmd(self, cmd):
	return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])
    def run_command(self, cmd):
 	output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	return output

