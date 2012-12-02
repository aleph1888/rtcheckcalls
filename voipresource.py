from twisted.web.resource import Resource
import subprocess

class VoipResource(Resource):
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
	dialplan = self.run_asterisk_cmd('dialplan show').split("\n")
	output = self.run_asterisk_cmd('sip show peers')
	lines = output.split("\n")
	res = "<pre>"+lines[0]+"\n</pre>"
	res = res.replace("[0;37m", "")
	res = res.replace("[0m", "")
	res_local = ""
	res_channels = ""
	res_end = ""
	for line in lines[1:]:
		if "OK" in line and "192.168." in line:
			line = self.add_ip_href(line)
			ext = self.get_extension(line, dialplan)
			res_local += line+" <b>"+ext+"</b>\n"
		elif "OK" in line:
			res_channels += line+"\n"
		else:
			ext = self.get_extension(line, dialplan)
			res_end += line+" <b>"+ext+"</b>\n"
	res += "<pre>"
	res += "<h2>Local</h2>"
	res += res_local
	res += "</pre><pre>"
	res += "<h2>Channels</h2>"
	res += res_channels
	res += "</pre><pre>"
	res += "<h2>Other</h2>"
	res += res_end
	res += "</pre><pre>"
	res += "<h2>Calls</h2>"
	res += self.run_asterisk_cmd('core show calls')
	res += "</pre><pre>"
	res += self.run_asterisk_cmd('core show uptime')
	res += "</pre>"
        return "<html><body>%s</body></html>" % (res,)
    def run_asterisk_cmd(self, cmd):
	return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])
    def run_command(self, cmd):
 	output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	return output

