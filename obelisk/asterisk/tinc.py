import os
from collections import defaultdict

TINC_DIR = "/etc/tinc/pln/"

class Tinc(object):
	def __init__(self):
		self.name = ""
		self.nodes = {}
		self.pubkey = ""
		f = open(os.path.join(TINC_DIR, "tinc.conf"))
		lines = f.readlines()
		f.close()
		for line in lines:
			parts = line.split("=")
			if len(parts) >= 2:
				key = parts[0].strip()
				value = parts[1].strip()
				if key == 'Name':
					self.name = value
					keydata = self.parse_key(value)
					self.pubkey = keydata['pubkey']
					self.address = keydata['address']
				elif key == 'ConnectTo':
					self.nodes[value] = self.parse_key(value)

	def parse_key(self, name):
		result = {}
		f = open(os.path.join(TINC_DIR, "hosts", name))
		pubkey = f.read()
		f.close()
		subnet_idx = pubkey.find('Subnet')
		if not subnet_idx == -1:
			result['subnet'] = pubkey[pubkey.find('=', subnet_idx)+1: pubkey.find('\n', subnet_idx)].strip()
		address_idx = pubkey.find('Address')
		if not address_idx == -1:
			result['address'] = pubkey[pubkey.find('=', address_idx)+1: pubkey.find('\n', address_idx)].strip()
		result['pubkey'] = pubkey[pubkey.find('---'):]
		return result

	def add_node(self, name, pubkey, address, hostname=False):
		dest_dir = os.path.join(TINC_DIR, "hosts", name)
		if not os.path.exists(dest_dir):
			f = open(dest_dir, 'w')
			f.write('Subnet = %s\n' % (address,))
			if hostname:
				f.write('Address = %s\n' % (hostname,))
			f.write(pubkey)
			f.close()


if __name__ == '__main__':
	t = Tinc()
	print t.name, t.address, t.pubkey
	for key, node in t.nodes.iteritems():
		print key, node.get('subnet', False), node.get('address', False)

