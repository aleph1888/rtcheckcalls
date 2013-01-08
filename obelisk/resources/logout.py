from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk.model import Model, WebSession

class LogoutResource(Resource):
    def render_GET(self, request):
	session_id = str(request.getSession().uid)
	request.getSession().expire()
	model = Model()
	web_session = model.query(WebSession).filter_by(session_id=session_id).first()
	if web_session:
		model.session.delete(web_session)
		model.session.commit()
        return redirectTo("/", request)

