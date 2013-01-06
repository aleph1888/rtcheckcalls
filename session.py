from model import Model, WebSession

def get_user(request):
	model = Model()
	session_id = str(request.getSession().uid)
        web_session = model.query(WebSession).filter_by(session_id=session_id).first()
	if web_session:
		return web_session.user


def get_session(request):
	session_id = str(request.getSession().uid)
	return session_id
