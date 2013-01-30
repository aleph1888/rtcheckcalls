from twisted.internet.task import deferLater
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.util import redirectTo
from twisted.web import server

from datetime import datetime
import time
import json

from obelisk.config import config
from obelisk.model import Model, WebSession, User
from obelisk.session import get_session, get_user, get_user_sessions
import obelisk.resources.peers
from obelisk.asterisk import ami

resource = None

class SSEConnection(object):
    def __init__(self, request):
	self.request = request
	self.session = get_session(request)
	self.user = get_user(request)
	request.transport.setTcpNoDelay(True)
	request.transport.setTcpKeepAlive(True)
	request.setHeader('Content-Type', 'text/event-stream')
	request.setHeader('Cache-Control', 'no-cache')
	request.setHeader('Connection', 'keep-alive')
	if self.user:
		self.write(time.time(), json.dumps({'user': self.user.voip_id, 'credit':float(self.user.credit)}), 'credit')
	self.write(time.time(), obelisk.resources.peers.resource.get_peers(), 'peers')

    def write(self, id, msg, section):
	self.request.write("id: %s\n" % (id,))
	self.request.write("event: %s\n" % (section,))
	if msg.__class__ == str:
		self.request.write("data: %s\n\n" % (msg,))
	else:
		self.request.write("data: %s\n\n" % (json.dumps(msg),))

class SSEResource(Resource):
    def __init__(self):
	global resource
	resource = self
	Resource.__init__(self)
	self._connections = {}
	ami.connector.registerEvent('CEL', self.onCelEvent)

    def onCelEvent(self, event):
	self.notify(event, 'rtcheckcalls', 'all')

    def getChild(self, name, request):
        return self

    def notify(self, value, section, user):
	sessions = []
	if user == 'all':
		sessions = 'all'
	elif user:
		sessions = get_user_sessions(user)
		sessions = map(lambda s: s.session_id, sessions)
	self.notifyChildren(value, section, sessions)

    def notifyChildren(self, value, section='message', sessions=[]):
	model = Model()
	for req in self._connections.keys():
		if req._disconnected:
			print "sse client disconnected", req
			self._connections.pop(req)
		else:
			conn = self._connections[req]
			web_session = model.query(WebSession).filter_by(session_id=conn.session).first()
			if sessions == 'all' or (conn.session in sessions) or (web_session and web_session.user and web_session.user.admin):
			#if not sessions or (conn.session in sessions) or (web_session and web_session.user and web_session.user.admin):
				if value.__class__ == str:
					conn.write(time.time(), value, section)
				else:
					conn.write(time.time(), json.dumps(value), section)

    def _delayedRender(self, request):
	if request in self._connections:
		conn = self._connections[request]
	else:
		conn = SSEConnection(request)
		self._connections[request] = conn

    def render_GET(self, request):
	logged = get_user(request)
	if True or (logged and logged.admin):
		d = deferLater(reactor, 1, lambda: request)
		d.addCallback(self._delayedRender)
		return server.NOT_DONE_YET
	return redirectTo("/", request)

