filename = "/etc/asterisk/prefixes.conf"


def list_prices():
	f = open(filename, "r")

	output = ""
	prices = {}

	label = ""
	for line in f.readlines():
		if line.startswith("["):
			label = line[1:line.find("]")]
			label = label.rsplit("-", 1)[0]
		# exten => _0035537[12345678]X.,1,Macro(callto,${albania-fix-provider}/${EXTEN},120,0.046)
		if "callto" in line:
			call_type = "unknown"
			if "-fix-" in line:
				call_type = "fix"
			elif "-mob-" in line:
				call_type = "mob"
			if not len(line.split(",")) >= 6:
				continue
			price = line[line.rfind(",")+1:line.rfind(")")]
			if not label in prices:
				prices[label] = {}
			prices[label][call_type] = price


	labels = prices.keys()
	labels.sort()
	for label in labels:
		output += "<h2>"+label+"</h2>"
		for call_type in prices[label]:
			price = prices[label][call_type]
			if price == "0.0":
				price = "gratis"
			else:
			   price = float(price) + 0.001
			output += call_type + ": " + str(price) + "<br />"

	f.close()
	return output

if __name__ == "__main__":
	print prices_list()
