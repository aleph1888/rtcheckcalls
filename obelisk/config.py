import json

f = open('config.json')
data = f.read()
f.close()
config = json.loads(data)

def clean_dict(adict):
	for key in adict.keys():
		value = adict[key]
		if value.__class__ == dict:
			clean_dict(value)
		else:
			value = str(value)
		del adict[key]
		adict[str(key)] = value


clean_dict(config)

if not 'host' in config:
	config['host'] = 'localhost'

