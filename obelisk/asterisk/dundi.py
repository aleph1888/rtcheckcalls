from collections import defaultdict
from urllib2 import urlopen
import os

from obelisk.asterisk.cli import run_command

FILE1 = "/etc/asterisk/dundi.conf"
FILE2 = "/etc/asterisk/dundi-extensions.conf"
FILE3 = "/etc/asterisk/sip/dundi.conf"
KEYS_DIR = "/var/lib/asterisk/keys/"

class Dundi(object):
	def __init__(self):
		self.outkey = ""
		self.hosts = {}
		self.parse_config()
		self.parse_extensions()
		self.parse_connections()
	def get_public_key(self):
		return self.outkey
	def parse_connections(self):
		connections = {}
		data = run_command('dundi show peers')
		lines = data.split("\n")[1:-1]
		for line in lines:
			eid = line[0:21].strip()
			host = line[21:31].strip()
			port = line[41:48].strip()
			status = line[68:].strip()
			if 'OK' in status:
				ping = float(status[status.find('(')+1:status.find(' ms')])/1000.0
				status = 'OK'
			elif 'LAGGED' in status:
				ping = float(status[status.find('(')+1:status.find(' ms')])/1000.0
				status = 'LAGGED'
			else:
				ping = False
			connections[host] = {'host': host, 'status': status, 'ping': ping, 'eid': eid}
		self.connections = connections
		return connections
	def has_node(self, ip):
		self.parse_connections()
		if ip in self.connections:
			return self.connections[ip]['ping']
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
				if key == 'outkey' and not self.outkey:
					f = open(os.path.join(KEYS_DIR, value + '.pub'))
					key_data = f.read()
					f.close()
					self.outkey = key_data
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
		if self.hosts:
			return self.hosts
		hosts = {}
		for a in range(256):
			exten = "+00%s00@pln" % (a,)
			res = run_command("dundi lookup " + exten)
			if "EXISTS" in res:
				node_id = res[res.find('from')+5:res.find(", expires")]
				addr = res[res.find('SIP'):res.find(" (EX")]
				ip = addr.split("/")[1].split(":")[0]
				try:
					url = urlopen("http://%s" % (ip,), timeout=1)
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
		self.hosts = hosts
		return hosts

if  __name__ == "__main__":
	d = Dundi()
	d.parse_extensions()
	d.parse_config()

