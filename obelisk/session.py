from obelisk.model import Model, WebSession, User

def get_user(request):
	model = Model()
	session_id = str(request.getSession().uid)
        web_session = model.query(WebSession).filter_by(session_id=session_id).first()
	if web_session:
                web_session.user.update_wallet(model)
		return web_session.user

def get_user_sessions(user):
	model = Model()
        web_sessions = model.query(WebSession).filter_by(user=user)
	return web_sessions


def get_session(request):
	session_id = str(request.getSession().uid)
	return session_id
