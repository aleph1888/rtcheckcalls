from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from datetime import datetime

import md5

from obelisk.config import config
from obelisk.asterisk.users import parse_users
from obelisk.model import Model, WebSession, User

resource = None

class LoginResource(Resource):
    def __init__(self):
	global resource
	Resource.__init__(self)
	resource = self
    def render_GET(self, request):
        return redirectTo("/", request)

    def render_POST(self, request):
	action = request.args['action'][0]
	login = request.args['login'][0]
	password = request.args['password'][0]
	return self.login(login, password, request)

    def check_password_ext(self, user_ext, password):
	users, passwords = parse_users("/etc/asterisk/sip.conf")
	username = users[user_ext]
	return self.check_password(username, password, users, passwords)

    def check_password(self, username, password, users=None, passwords=None):
	if not users or not passwords:
		users, passwords = parse_users("/etc/asterisk/sip.conf")
	user_input = md5.new(username + ":asterisk:" + password).hexdigest()
	if username in passwords and user_input == passwords[username]:
		ext = ""
		for user_ext in users:
			if users[user_ext] == username:
				ext = user_ext
		return ext
	return False

    def login(self, login, password, request, email=''):
	user_ext = self.check_password(login, password)
	if user_ext:
		model = Model()
		user = model.get_user_fromext(user_ext)
		if not user:
			user = User(user_ext)
			if email:
				user.email = email
			model.session.add(user)
			model.session.commit()
		session_id = str(request.getSession().uid)
		web_session = model.query(WebSession).filter_by(session_id=session_id).first()
		if not web_session:
			web_session = WebSession(session_id=session_id, timestamp=datetime.now(), user=user)

		model.session.add(web_session)
		model.session.commit()
		return redirectTo("/user/"+user_ext, request)
	return redirectTo("/", request)
