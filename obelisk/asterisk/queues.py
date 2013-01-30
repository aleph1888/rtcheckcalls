from collections import defaultdict

filename = '/etc/asterisk/queues.conf'

def get_queues():
	f = open(filename)

	section = ""

	queues = defaultdict(list)

	for line in f.readlines():
		if line.startswith("["):
			section = line[1:line.find("]")]
		if line.startswith("member"):
			member = line.split("=")[1].strip()
			member = member.split("/")[1].split("@")[0]
			queues[section].append(member)


	f.close()
	return queues

if __name__ == '__main__':
	print get_queues()
