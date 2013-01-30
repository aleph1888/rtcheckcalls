import json

filename = "/etc/asterisk/prefixes.conf"

from obelisk.pricechecker import get_winners

def parse_prices():
	f = open(filename, "r")

	prices = {}
	label = ""
	label_price = ""
	type = ""
	for line in f.readlines():
		
		if line.startswith(";"):
			pass
		elif line.startswith("["):
			label = line[1:line.find("]")]
			label_parts = label.rsplit("-", 1)
			label = label_parts[0]
			label_price = ""
			type = label_parts[1]
		# exten => _0035537[12345678]X.,1,Macro(callto,${albania-fix-provider}/${EXTEN},120,0.046)
		elif "callto" in line:
			call_type = "unknown"
			price = line[line.rfind(",")+1:line.rfind(")")]
			if label_price == "":
				label_price = price
			elif price != label_price:
				print "price mismatch for", label, price, label_price
			provider = line[line.find('$')+2: line.find('provider')+8]
			if not len(line.split(",")) >= 6:
				continue
			if not label in prices:
				prices[label] = {}
			if type == 'fixmob':
				prices[label]['fix'] =  [price, provider]
				prices[label]['mob'] =  [price, provider]
			else:
				prices[label][type] =  [price, provider]
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
			price, provider = prices[label][call_type]
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
			price, provider  = prices[label][call_type]
			if price == "0.0":
				price = "'gratis'"
			else:
			   price = float(price) + 0.001
			output += "'" + call_type + "': " + str(price) + ","
		output += "},"
	output += "}"
	return output


if __name__ == "__main__":
	parse_prices()
	print list_prices_json()
