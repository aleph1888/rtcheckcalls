import subprocess
import sha
import time
import md5

user_template = """
[%%username%%](payuser)
regexten=%%ext%%
username=%%username%%
md5secret=%%password%%
callerid=%%username%% <%%ext%%>
"""

def get_options(user_ext):
	extensions, passwords = parse_users("/etc/asterisk/sip.conf")
	username = extensions[user_ext]
	f = open("/etc/asterisk/sip.conf")
	data = f.readlines()
	f.close()
	options = {'srtp': False, 'tls': False, 'codecs': []}
	for line in data:
		if line.startswith('[' + username):
			our_section = True
		elif line.startswith("["):
			our_section = False
		elif not our_section:
			continue
		elif line.startswith("encryption"):
			if line.split("=")[1].strip() == 'yes':
				options['srtp'] = True
			continue
		elif line.startswith("transport"):
			if line.split("=")[1].strip() == 'tls':
				options['tls'] = True
		elif line.startswith("disallow"):
			if line.split("=")[1].strip() == 'all':
				options['codecs'] = []
		elif line.startswith("allow"):
			codec = line.split("=")[1].strip()
			options['codecs'].append(codec)
	return options

def change_options(user_ext, options):
	extensions, passwords = parse_users("/etc/asterisk/sip.conf")
	username = extensions[user_ext]
	f = open("/etc/asterisk/sip.conf")
	data = f.readlines()
	f.close()
	output = ""
	newcodecs = False
	if 'codecs' in options:
		newcodecs = options['codecs']
	tls = False
	if 'tls' in options:
		tls = options['tls']
	srtp = False
	if 'srtp' in options:
		srtp = options['srtp']
	our_section = False
	tlsdone = False
	srtpdone = False
	codecsdone = False
	for line in data:
		if line.startswith('[' + username):
			our_section = True
		elif line.startswith("["):
			our_section = False
		elif not our_section:
			output += line
			continue
		elif line.startswith("encryption") or line.startswith("transport") or line.startswith("port"):
			tlsfound = True
			continue
		elif line.startswith("allow") or line.startswith("disallow"):
			codecsfound = True
			continue
		elif ('secret' in line or 'md5secret' in line) and our_section and 'password' in options:
			pass_string = "%s:asterisk:%s" % (username, options['password'])
			hashed = md5.new(pass_string).hexdigest()
			line = "md5secret=%s\n" % (hashed,)
		if newcodecs and not line.strip() and not codecsdone:
			output += "disallow=all\n"
			for codec in newcodecs:
				output += "allow=%s\n" % (codec,)
			codecsdone = True
		if not line.strip() and tls and not tlsdone:
			output += "transport=tls\n"
			output += "port=5061\n"
			tlsdone = True
		if not line.strip() and srtp and not srtpdone:
			output += "encryption=yes\n"
			srtpdone = True
					
		output += line
	f = open("/etc/asterisk/sip.conf."+str(time.time())+".bak", 'w')
	f.writelines(data)
	f.close()
	f = open("/etc/asterisk/sip.conf", 'w')
	f.write(output)
	f.close()


def change_password(user_ext, password):
	extensions, passwords = parse_users("/etc/asterisk/sip.conf")
	username = extensions[user_ext]
	f = open("/etc/asterisk/sip.conf")
	data = f.readlines()
	f.close()
	output = ""
	our_section = False
	for line in data:
		if line.startswith('[' + username):
			our_section = True
		elif line.startswith("["):
			our_section = False
		elif ('secret' in line or 'md5secret' in line) and our_section:
			pass_string = "%s:asterisk:%s" % (username, password)
			hashed = md5.new(pass_string).hexdigest()
			line = "md5secret=%s\n" % (hashed,)
		output += line
	f = open("/etc/asterisk/sip.conf."+str(time.time())+".bak", 'w')
	f.writelines(data)
	f.close()
	f = open("/etc/asterisk/sip.conf", 'w')
	f.write(output)
	f.close()

def add_extension(username, extension):
	f = open("/etc/asterisk/extensions.conf")
	data = f.readlines()
	f.close()
	f = open("/etc/asterisk/extensions.conf."+str(time.time())+".bak", 'w')
	f.writelines(data)
	f.close()
	output = ""
	section = "to-internal"
	our_section = False
	for line in data:
		if line.startswith('['+section):
			our_section = True
		elif line.startswith('['):
			our_section = False
		elif not line.strip() and our_section:
			output +=  "exten => %s,1,Dial(SIP/%s)\n" % (extension, username)
			our_section = False
		output += line
	f = open("/etc/asterisk/extensions.conf", 'w')
	f.write(output)
	f.close()

def create_user(username, password):
	f = open("/etc/asterisk/sip.conf")
	data = f.readlines()
	f.close()
	f = open("/etc/asterisk/sip.conf."+str(time.time())+".bak", 'w')
	f.writelines(data)
	f.close()
	maxexten = 0
	username_avail = 1
	for line in data:
		if line.startswith('regexten'):
			exten = int(line.split('=')[1].strip())
			if exten < 9999 and exten > maxexten:
				maxexten = exten
		elif line.startswith('username'):
			_username = line.split('=')[1].strip()
			if _username == username:
				username_avail = False
	if not username_avail:
		print "username already taken", username
		return False
	password = md5.new("%s:asterisk:%s" % (username, password)).hexdigest()
	nextexten = maxexten + 1
	user_data = user_template.replace('%%ext%%', str(nextexten))
	user_data = user_data.replace('%%username%%', username)
	user_data = user_data.replace('%%password%%', password)
	add_extension(username, maxexten+1)
	f = open("/etc/asterisk/sip.conf", 'a')
	f.write(user_data)
	f.close()
	output = subprocess.Popen(['/etc/init.d/asterisk', 'reload'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	print "user created", username, maxexten + 1
	return user_data

def parse_users(filename):
	from obelisk.config import config
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
		pass_string = "%s:asterisk:%s" % (section, password)
		hashed = md5.new(pass_string).hexdigest()
		passwords[section] = hashed
	    if line.startswith("md5secret"):
		password = line.split("=")[1].strip()
		passwords[section] = password
	return extensions, passwords


if __name__ == "__main__":
    print parse_users("/etc/asterisk/sip.conf")
    #print create_user('foobar2', 'xxx')
    #print change_password('caedes_roam', 'xxx')
