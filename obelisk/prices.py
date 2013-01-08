filename = "/etc/asterisk/prefixes.conf"

def parse_prices():
	f = open(filename, "r")

	prices = {}
	label = ""

	for line in f.readlines():
		if line.startswith("["):
			label = line[1:line.find("]")]
			label = label.rsplit("-", 1)[0]
		# exten => _0035537[12345678]X.,1,Macro(callto,${albania-fix-provider}/${EXTEN},120,0.046)
		if "callto" in line:
			call_type = "unknown"
			price = line[line.rfind(",")+1:line.rfind(")")]
			if not len(line.split(",")) >= 6:
				continue
			if not label in prices:
				prices[label] = {}
			if "-fix-" in line:
				prices[label]['fix'] = price
			elif "-mob-" in line:
				prices[label]['mob'] = price
			elif "-fixmob-" in line:
				prices[label]['fix'] = price
				prices[label]['mob'] = price
	f.close()
	return prices

def list_prices():
	prices = parse_prices()
	labels = prices.keys()
	labels.sort()
	output = ""

	for label in labels:
		output += "<h2>"+label+"</h2>"
		for call_type in prices[label]:
			price = prices[label][call_type]
			if price == "0.0":
				price = "gratis"
			else:
			   price = float(price) + 0.001
			output += call_type + ": " + str(price) + "<br />"
	return output

def list_prices_json():
	prices = parse_prices()
	labels = prices.keys()
	labels.sort()
	output = "{"

	for label in labels:
		output += "'"+label+"': {"
		for call_type in prices[label]:
			price = prices[label][call_type]
			if price == "0.0":
				price = "'gratis'"
			else:
			   price = float(price) + 0.001
			output += "'" + call_type + "': " + str(price) + ","
		output += "},"
	output += "}"
	return output

if __name__ == "__main__":
	print prices_list()
