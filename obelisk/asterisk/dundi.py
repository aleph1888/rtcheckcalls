from collections import defaultdict
from urllib import urlopen

from obelisk.asterisk.cli import run_command

FILE1 = "/etc/asterisk/dundi.conf"
FILE2 = "/etc/asterisk/dundi-extensions.conf"
FILE3 = "/etc/asterisk/sip/dundi.conf"

class Dundi(object):
	def __init__(self):
		self.parse_config()
		self.parse_extensions()
	def parse_config(self):
		f = open(FILE1)
		lines = f.readlines()
		f.close()
		data = defaultdict(dict)
		for line in lines:
			if line.startswith("["):
				section = line[1:line.find("]")].strip()
			elif line.startswith(";"):
				pass
			elif "=>" in line:
				pass
			elif "=" in line:
				pars = line.split("=", 1)
				key = pars[0].strip()
				value = pars[1].strip()
				data[section][key] = value
		self.config = data
	def parse_extensions(self):
		f = open(FILE2)
		lines = f.readlines()
		f.close()
		section = ""
		geo_set = set()
		nongeo_set = set()
		for line in lines:
			if line.startswith("["):
				section = line[1:line.find("]")].strip()
			if section == "pln-to-internal" and line.startswith("exten"):
				exten = line.split("=>")[1].split(",")[0].strip().strip("_")
				exten = exten.replace("+", "00")
				geo = False
				if exten.startswith("0000"):
					exten = exten[4:]
				elif exten.startswith("000"):
					exten = exten[3:]
					geo = True
				if exten.endswith("X"):
					exten = exten.strip("X")
				elif exten.endswith("0"):
					exten = exten[:-1]
				else:
					print "unknown pattern", exten
				if exten.endswith("0"):
					# ok, separator
					exten = exten[:-1]
				else:
					print "cant parse extension", line
				if geo:
					geo_set.add(exten)
				else:
					nongeo_set.add(exten)
		self.geo = list(geo_set)
		self.nongeo = list(nongeo_set)
	def find_hosts(self):
		hosts = {}
		for a in range(256):
			exten = "+00%s00@pln" % (a,)
			res = run_command("dundi lookup " + exten)
			if "EXISTS" in res:
				node_id = res[res.find('from')+5:res.find(", expires")]
				addr = res[res.find('SIP'):res.find(" (EX")]
				ip = addr.split("/")[1].split(":")[0]
				try:
					url = urlopen("http://%s" % (ip,))
				except:
					continue
				if url:
					data = url.read()
					url.close()
				else:
					data = False
				hosts[node_id] = {'host': ip, 'nongeo': a, 'id': node_id, 'web': data}
		for name, node in self.config.iteritems():
			if name == 'general':
				continue
			if name in hosts:
				hosts[name].update(node)
			else:
				hosts[name] = node
		return hosts

if  __name__ == "__main__":
	d = Dundi()
	d.parse_extensions()
	d.parse_config()

