from collections import defaultdict

FILE1 = "/etc/asterisk/dundi.conf"
FILE2 = "/etc/asterisk/dundi-extensions.conf"
FILE3 = "/etc/asterisk/sip/dundi.conf"

class Dundi(object):
	def __init__(self):
		pass
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
		print data.keys(), data["general"]
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
		print "geo", geo_set	
		print "nongeo", nongeo_set	

if  __name__ == "__main__":
	d = Dundi()
	d.parse_extensions()
	d.parse_config()

