from incf.countryutils import transformations

from obelisk.asterisk.providers import get_providers
from obelisk.pricechecker import get_winners, load_provider
from obelisk.asterisk.prefixes import parse_prices

def normalize_price(price):
	if price == 'FREE*':
		price = 0.0
	return float(price)

def check_prices():
	prices = parse_prices()
	#provider_prices = load_provider(name)
	providers = get_providers()
	loaded_providers = {}
	winners = get_winners()
	better_deal = ""
	countries = prices.keys()
	countries.sort()
	for country in countries:
		for type in prices[country]:
			current_rate, provider_code = prices[country][type]
			if provider_code in providers:
				if provider_code in loaded_providers:
					provider_prices = loaded_providers[provider_code]
				else:
					names = providers[provider_code]
					if names.__class__ ==  str:
						names = [names]
					all_prices = []
					for name in names:
						if name in ['freevoipdeal2', 'freevoipdeal3']:
							name = 'freevoipdeal'
						# XXX check if prices are the same for given country...
						provider_prices = load_provider(name)
						loaded_providers[provider_code] = provider_prices
						try:
							country_price = normalize_price(provider_prices[country][type])
							all_prices.append(country_price)
						except:
							print "problem with", name, country, type
					ok = True
					if all_prices:
						last_price = all_prices[0]
						for aprice in all_prices:
							if aprice != last_price:
								print "Price inconsistency", country, type, all_prices
								ok = False
					else:
						print "No prices for", name, country, type
				if country in provider_prices and type in provider_prices[country]:
					try:
						country_name = transformations.ccn_to_cn(transformations.cca2_to_ccn(country))
					except:
						country_name = 'Unknown'
					current_rate = float(current_rate)
					names = providers[provider_code]
					provider_rate = normalize_price(provider_prices[country][type])
					if current_rate != provider_rate:
						key = country + " " + type
						if key in winners:
							print country_name + " ["+country+"]\t"+type, current_rate, provider_rate, providers[provider_code], winners[key]
						else:
							print country_name + " ["+country+"]\t"+type, current_rate, provider_rate, providers[provider_code]
					else:
						key = country + " " + type
						if key in winners:
							winner_rate = normalize_price(winners[key][0])
							if winner_rate < current_rate:
								better_deal += "%s [%s]\t%s %s %s %s %s\n" % (country_name, country, type, current_rate, providers[provider_code], winner_rate, str(winners[key][1]))
						
				else:
					print country, type, "not available"
			else:
				print "unknown", provider_code
	print "BETTER DEALS"
	print better_deal
		

if __name__ == "__main__":
	check_prices()
