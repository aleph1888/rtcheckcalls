import json

f = open('config.json')
data = f.read()
f.close()
config = json.loads(data)

for key in config.keys():
	value = str(config[key])
	del config[key]
	config[str(key)] = value

if not 'host' in config:
	config['host'] = 'localhost'

