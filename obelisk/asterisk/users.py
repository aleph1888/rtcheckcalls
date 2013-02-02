import subprocess
import time
import md5

from obelisk.asterisk.model import SipPeer, Extension, VoiceMail
from obelisk.model import Model

def reload_asterisk(peer_name):
	output = subprocess.Popen(['/usr/sbin/asterisk', '-nrx', 'sip prune realtime peer ' + peer_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	print output
	output = subprocess.Popen(['/usr/sbin/asterisk', '-nrx', 'sip show peer ' + peer_name + ' load'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

def reload_peers():
	model = Model()
	peers = model.query(SipPeer)
	for peer in peers:
		reload_asterisk(peer.name)

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
	exten = model.query(Extension).filter_by(exten=peer.regexten).first()
	if exten.app == 'Gosub':
		options['voicemail'] = True
	else:
		options['voicemail'] = False
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
	else:
		peer.disallow = ''
		peer.allow = ''
	# tls
	if  options.get('tls', False):
		peer.transport = 'tls'
	else:
		peer.transport = 'udp'
	# srtp
	if options.get('srtp', False):
		peer.encryption = 'yes'
	else:
		peer.encryption = 'no'
	# voicemail
	exten = model.query(Extension).filter_by(exten=peer.regexten).first()
	if options.get('voicemail', False):
		exten.app = 'Gosub'
		exten.appdata = 'stdexten,%s,1(SIP/%s,default)' % (peer.regexten, peer.name)
	else:
		exten.app = 'Dial'
		exten.appdata = 'SIP/%s,60' % (peer.name,)
	exten_sip = model.query(Extension).filter_by(exten=peer.name).first()
	exten_sip.app = exten.app
	exten_sip.appdata = exten.appdata
	model.session.commit()
	# reload asterisk
	reload_asterisk(peer.name)
	return True


def change_password(user_ext, password):
	model = Model()
	peer = model.query(SipPeer).filter_by(regexten=user_ext).first()
	pass_string = "%s:asterisk:%s" % (peer.name, password)
	hashed = md5.new(pass_string).hexdigest()
	peer.md5secret = hashed
	peer.secret = ''
	model.session.commit()
	# reload asterisk
	reload_asterisk(peer.name)

def add_extension(username, extension):
	model = Model()
	new_extension = Extension('to-internal', extension, 1, 'Gosub', 'stdexten,%s,1(SIP/%s,default)' % (extension, username))
	new_extension2 = Extension('to-internal-sip', username, 1, 'Gosub', 'stdexten,%s,1(SIP/%s,default)' % (extension, username))
	new_voicemail = VoiceMail(context='default', mailbox=extension, password='5555')
	model.session.add(new_extension)
	model.session.add(new_extension2)
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
	reload_asterisk(peer.name)
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
