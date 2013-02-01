from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Sequence, Numeric, DateTime, Float, ForeignKey, Text, Boolean, SmallInteger, Enum, LargeBinary
from sqlalchemy.dialects.mysql import TINYINT

import time

class VoiceMailMessage(Base):
	__tablename__ = 'voicemail_messages'
	dir = Column(String(255), primary_key=True)
	msgnum = Column(Integer(4), primary_key=True)
	context = Column(String(80))
	macrocontext = Column(String(80))
	callerid = Column(String(80))
	origtime = Column(Integer(11))
	duration = Column(Integer(11))
	mailboxuser = Column(String(30))
	mailboxcontext = Column(String(30))
	msg_id = Column(String(40))
	recording = Column(LargeBinary())
	def __repr__(self):
		return "<VoiceMailMessage('%s', '%s', %s, %ss, %skB)>" % (self.mailboxuser, self.callerid, time.ctime(self.origtime), self.duration, len(self.recording)/1024)


class VoiceMail(Base):
	__tablename__ = 'voicemail'
	uniqueid = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	context = Column(String(80), default='default', nullable=False)
	mailbox = Column(String(80), nullable=False)
	password = Column(String(80), nullable=False)
	fullname = Column(String(80))
	email = Column(String(80))
	pager = Column(String(80))
	language = Column(String(20))
	def __repr__(self):
		return "<VoiceMail('%s', '%s', %s, '%s', '%s')>" % (self.context, self.mailbox, self.password, self.fullname, self.email)


class Extension(Base):
	__tablename__ = 'extensions'
	id = Column(Integer, Sequence('extension_id_seq'), primary_key=True)
	context = Column(String(20), default='')
	exten = Column(String(20), default='')
	priority = Column(TINYINT(4), default=0)
	app = Column(String(20), default='')
	appdata = Column(String(256), default='')
	def __init__(self, context, exten, priority, app, appdata):
		self.context = context
		self.exten = exten
		self.priority = priority
		self.app = app
		self.appdata = appdata
	def __repr__(self):
		return "<Extension('%s', '%s', %s, '%s', '%s')>" % (self.context, self.exten, self.priority, self.app, self.appdata)
	
class SipPeer(Base):
	__tablename__ = 'sippeers'
	#__table_args__ = {
	#	'mysql_engine': 'InnoDB',
	#	'mysql_charset': 'utf8'
	#}
	id = Column(Integer, Sequence('sippeer_id_seq'), primary_key=True)
	name = Column(String(10), nullable=False, unique=True)
	callerid = Column(String(80))
	ipaddr = Column(String(15))
	port = Column(Integer(5))
	regseconds = Column(Integer(11))
	useragent = Column(String(128))
	lastms = Column(Integer(11))
	host = Column(String(40))
	type = Column(Enum('friend', 'peer', 'user'))
	context = Column(String(40))
	secret = Column(String(40))
	md5secret = Column(String(40))
	transport = Column(String(40))
	directmedia = Column(Enum('yes', 'no', 'nonat', 'update'))
	nat = Column(Enum('yes', 'no', 'never', 'route'))
	language = Column(String(40))
	disallow = Column(String(40))
	allow = Column(String(40))
	mailbox = Column(String(40))
	regexten = Column(String(40))
	qualify = Column(String(40))
	hasvoicemail = Column(Enum('yes', 'no'))
	encryption = Column(Enum('yes', 'no'))
	avpf = Column(Enum('yes', 'no'))
	directrtpsetup = Column(Enum('yes', 'no'))
	icesupport = Column(Enum('yes', 'no'))
	callbackextension = Column(String(40))
	sippasswd = Column(String(80))
	insecure = Column(String(40))
	fullcontact = Column(String(80))
	def __repr__(self):
		return "<SipPeer('%s', '%s', %s, '%s', '%s')>" % (self.name, self.regexten, self.useragent, self.transport, self.encryption)


