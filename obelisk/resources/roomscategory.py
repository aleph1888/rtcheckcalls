from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import session
from obelisk.model import Model

from obelisk.asterisk.rooms import newCATEGORY
from obelisk.session import get_user

from datetime import *

class RoomsCategoryResource(Resource):
  
  def render_POST(self, request):
	print "sssssssssssssssssssssssssssssssssss"
	#security check
	usrLogged = get_user(request)
	if not usrLogged:
		return redirectTo("/", request)
	
	stUserExten = usrLogged.voip_id

	#prepare to read _POST request
	yRequestArgs = {}
	yRoomArgs = {}
	for a in request.args:
    		yRequestArgs[a] = request.args[a][0]
	
	#Who sends post? First check View forms, after Data form.
	if yRequestArgs.get('hidfrmTreeAction') == 'NEWEXEC':
		#ACTION: NEW ROOM

		#set values
		print "guardar valor newCategory(" + yRequestArgs.get('txtNewCategory') + "/" + str(yRequestArgs.get('hidfrmTreeCodCategory', 0))
		nIdCategoryParent = yRequestArgs.get('hidfrmTreeCodCategory', 0)
		ncodCategory = newCATEGORY(yRequestArgs.get('txtNewCategory'), int(nIdCategoryParent))

		#skip	
		return redirectTo('/rooms?hidfrmMyViewAction=FILTER&codCategoryFilterView=' + str(ncodCategory), request)

  def render_GET(self, request):
  
	return redirectTo('/rooms', request)


