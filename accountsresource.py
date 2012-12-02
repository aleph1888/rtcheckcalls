from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from accounting import accounting
import subprocess
from datetime import datetime
import csv

class AccountResource(Resource):
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

	if 'account' in args:
		res = args['account']
	else:
		parts = request.path.split("/")
		if len(parts) > 2:
			user = parts[2]
			if user == 'addcredit':
				self.add_credit(parts[3:])
				return redirectTo("/user/" + parts[3], request)
			else:
				res = self.render_user(user)
        return "<html><body>%s</body></html>" % (res,)
    def add_credit(self, args):
	user = args[0]
	credit = float(args[1])
	accounting.add_credit(user, credit)
    def render_user(self, user):
	res = user
	if user in self._accounting._data:
		res += "<p>Tu saldo es "+str(self._accounting._data[user])+"</p>"
	res += self.render_user_calls(user)
	return res
    def render_user_calls(self, user):
	FILE = "/var/log/asterisk/cdr-csv/Master.csv"
	f = open(FILE)
	csv_file = csv.reader(f)
	data = list(csv_file)
	res = "<h2>Llamadas</h2>"

	res += "<p>"
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
		delta = 0.0
		#totalsecs += int(billsecs)
		t1 = datetime.strptime(time_1, "%Y-%m-%d %H:%M:%S")
		to_ext = a[2]
		if time_3:
			t2 = datetime.strptime(time_3, "%Y-%m-%d %H:%M:%S")
			delta = t2-t1
		if from_ext == user or to_ext == user:
			calls = "<p>%s to %s for %s secs on %s/%s/%s</p>" % (from_ext, to_ext, delta, t1.day, t1.month, t1.year) + calls

		#if status == "ANSWERED" and (billsecs > umbra or not umbra):
		#	print from_ext,"->"," "*(14-len(a[2]))+a[2]+" ["+str(billsecs)+"]\t"+str(t1.day)+"\t"+str(t1.hour)
	res += calls
	res += "</p>"
	return res


    def getChild(self, name, request):
        return self
    def run_asterisk_cmd(self, cmd):
	return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])
    def run_command(self, cmd):
 	output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	return output

