from .queues import get_queues

def get_providers():
	providers = {}
	filename = '/etc/asterisk/providers.conf'

	f = open(filename)
	lines = f.readlines()
	f.close()

	queues = get_queues()

	for line in lines:
		if line.startswith(';') or not line.strip():
			pass
		elif '=' in line:
			parts = line.split('=')
			parts = map(lambda s: s.strip(), parts)
			provider_code = parts[0]
			if "/" in parts[1]:
				channel = parts[1].split('/')[1]
			else:
				channel = parts[1]
				if channel in queues:
					channel = queues[channel]
				else:
					print "channel does not exist", channel
				#channel = parts[1]
			providers[provider_code] = channel
	return providers


if __name__ == '__main__':
	print get_providers()
