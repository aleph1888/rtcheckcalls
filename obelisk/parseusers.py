
import sha
from obelisk.config import config

def parse_users(filename):
	f = open(filename)
	data = f.readlines()
	f.close()

	extensions = {}
	passwords = {}

	section = ""

	for line in data:
	    if line.startswith("["):
		section = line[1:line.find("]")]
	    if line.startswith("regexten"):
		ext = line.split("=")[1].strip()
		extensions[ext] = section
	    if line.startswith("secret"):
		password = line.split("=")[1].strip()
		passwords[section] = sha.new(password+config['secret']).hexdigest()
	return extensions, passwords


if __name__ == "__main__":
    print parse_users("/etc/asterisk/sip.conf")
