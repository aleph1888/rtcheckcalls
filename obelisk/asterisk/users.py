import subprocess
import time
import md5

from obelisk.asterisk.model import SipPeer, Extension, VoiceMail
from obelisk.model import Model

def get_options(user_ext):
	model = Model()
	peer = model.query(SipPeer).filter_by(regexten=user_ext).first()
	username = peer.name
	options = {'srtp': False, 'tls': False, 'codecs': []}
	if peer.encryption == 'yes':
		options['srtp'] = True
	if peer.transport == 'tls':
		options['tls'] = True
	if peer.disallow == 'all':
		options['codecs'] = []
	if peer.allow:
		options['codecs'] = peer.allow.split(',')
	return options

def change_options(user_ext, options):
	model = Model()
	peer = model.query(SipPeer).filter_by(regexten=user_ext).first()
	if not peer:
		return False
	username = peer.name
	# password
	if 'passwd' in options:
		pass_string = "%s:asterisk:%s" % (username, options['password'])
                hashed = md5.new(pass_string).hexdigest()
		peer.md5secret = hashed
		peer.secret = ''
	# newcodecs
	newcodecs = False
	if 'codecs' in options:
		newcodecs = options['codecs']
	if newcodecs:
		peer.disallow = 'all'
		peer.allow = ','.join(newcodecs)
	# tls
	tls = False
	if 'tls' in options:
		tls = options['tls']
	if  tls:
		peer.transport = 'tls'
	else:
		peer.transport = 'udp'
	# srtp
	srtp = False
	if 'srtp' in options:
		srtp = options['srtp']
	if srtp:
		peer.encryption = 'yes'
	else:
		peer.encryption = 'no'
	model.session.commit()
	# reload asterisk
	output = subprocess.Popen(['/etc/init.d/asterisk', 'reload'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
	return True


def change_password(user_ext, password):
	model = Model()
	peer = model.query(SipPeer).filter_by(regexten=user_ext).first()
	pass_string = "%s:asterisk:%s" % (username, password)
	hashed = md5.new(pass_string).hexdigest()
	peer.md5secret = hashed
	peer.secret = ''
	model.session.commit()
	# reload asterisk
	output = subprocess.Popen(['/etc/init.d/asterisk', 'reload'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]

def add_extension(username, extension):
	model = Model()
	new_extension = Extension('to-internal', extension, 1, 'Gosub', 'stdexten,%s,1(SIP/%s,default)' % (extension, username))
	new_voicemail = VoiceMail(context='default', mailbox=extension, password='5555')
	model.session.add(new_extension)
	model.session.add(new_voicemail)
	model.session.commit()

def create_user_internal(model, **kwargs):
	peer = SipPeer(**kwargs)
	model.session.add(peer)
	model.session.commit()
	add_extension(kwargs['name'], kwargs['regexten'])
	return peer

def create_user(username, password):
	username_avail = 1
	model = Model()

	# check if username is taken
	if model.query(SipPeer).filter_by(name=username).first():
		print "username already taken", username
		return False

	# find next available extension
	peers = model.query(SipPeer).order_by('regexten')
	maxexten = 0
	for peer in peers:
		exten = int(peer.regexten)
		if exten < 9999 and exten > maxexten:
			maxexten = exten

	nextexten = maxexten + 1

	# create user in database
	password = md5.new("%s:asterisk:%s" % (username, password)).hexdigest()
	peer = create_user_internal(model, regexten=str(nextexten),
			name=username,
			md5secret=password,
			callerid='%s <%s>' % (username, nextexten),
			type='peer',
			host='dynamic',
			nat='comedia,force_rport',
			qualify='yes',
			mailbox=str(nextexten),
			context="from-payuser")

	# reload asterisk
	output = subprocess.Popen(['/etc/init.d/asterisk', 'reload'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
	print "user created", username, nextexten
	return peer

def parse_users(filename=None):
	extensions = {}

	model = Model()
	peers = model.query(SipPeer).order_by('regexten')
	for peer in peers:
		extensions[peer.regexten] = peer.name

	return extensions


if __name__ == "__main__":
    print parse_users("/etc/asterisk/sip.conf")
    #print create_user('foobar2', 'xxx')
    #print change_password('caedes_roam', 'xxx')
