from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from datetime import datetime

import sha

from obelisk.config import config
from obelisk.parseusers import parse_users
from obelisk.model import Model, WebSession, User

class LoginResource(Resource):
    def __init__(self):
	Resource.__init__(self)
	self._users, self._passwords = parse_users("/etc/asterisk/sip.conf")
    def render_GET(self, request):
        return redirectTo("/", request)
    def render_POST(self, request):
	res = str(dict(request.args))
	action = request.args['action'][0]
	login = request.args['login'][0]
	password = request.args['password'][0]
	user_input = sha.new(password+config['secret']).hexdigest()
	if login in self._passwords and user_input == self._passwords[login]:
		res += " OK "

		ext = ""
		for user_ext in self._users:
			if self._users[user_ext] == login:
				ext = user_ext

		res += ext
		model = Model()
		user = model.get_user_fromext(ext)
		if not user:
			user = User(ext)
			model.session.add(user)
			model.session.commit()
		session_id = str(request.getSession().uid)
		web_session = model.query(WebSession).filter_by(session_id=session_id).first()
		if not web_session:
			web_session = WebSession(session_id=session_id, timestamp=datetime.now(), user=user)

		model.session.add(web_session)
		model.session.commit()
		return redirectTo("/user/"+ext, request)
	return redirectTo("/", request)
