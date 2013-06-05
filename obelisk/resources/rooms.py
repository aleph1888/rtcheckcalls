from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk import session
from obelisk.model import Model
from obelisk.templates import print_template
from obelisk.asterisk.rooms import cCONF_BASE_EXTEN,  cCONF_BASE_RECORDING, newROOM, getROOMS, getROOMCATEGORIES, newCATEGORY, getROOM, editROOM, deleteROOM, getROOMCATEGORIEStree, getConfbridgeStatusDictionaryOfUsersInRoom, getConfbridgeStatusListOfUsersForInputSelect, getConfbridgeStatus
from obelisk.session import get_user

from obelisk.asterisk import ami
from obelisk.resources import sse

from obelisk.asterisk import cli

from time import gmtime, strftime

from os import listdir, path, remove
from os.path import isfile, join, isdir

from obelisk.tools import html


class RoomsResource(Resource):
  
  
  def __init__(self):
        Resource.__init__(self)
	ami.connect()
	ami.connector.registerEvent('ConfbridgeStart', self.on_bridge_start)
	ami.connector.registerEvent('ConfbridgeJoin', self.on_bridge_join)
	ami.connector.registerEvent('ConfbridgeLeave', self.on_bridge_leave)
	ami.connector.registerEvent('ConfbridgeEnd', self.on_bridge_end)
	
  def on_bridge_start(self, event):
	sse.resource.notify(event, 'bridge_start', 'all')
 
  def on_bridge_join(self, event):
	yResults = getConfbridgeStatusDictionaryOfUsersInRoom(event["conference"]) 
	event["usersInRoom"] = yResults
	sse.resource.notify(event, 'bridge_join', 'all')

  def on_bridge_leave(self, event):
	yResults = getConfbridgeStatusDictionaryOfUsersInRoom(event["conference"]) 	
	event["usersInRoom"] = yResults
	sse.resource.notify(event, 'bridge_leave', 'all')

  def on_bridge_end(self, event):
	sse.resource.notify(event, 'bridge_end', 'all')

  def on_bridge_talking(self, event):
	sse.resource.notify(event, 'bridge_talking', 'all')

  def on_actionOK(self, stMessage):
	jsonMessage = {'info': stMessage}
	sse.resource.notify(jsonMessage, 'on_action', 'all')

  def on_actionOKRecording(self, stMessage, nExten):	
	jsonMessage = {'info':stMessage, 'audiolist': self.getAudioList(nExten)}
	sse.resource.notify(jsonMessage, 'on_action', 'all')

  def on_actionERR(self, stMessage):
	jsonMessage = {'info':stMessage}
	sse.resource.notify(jsonMessage, 'on_action', 'all')	
	
  def getUniqueIdFromDate(self):
	stUniqueId = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	stUniqueId = stUniqueId.replace(":","")
	stUniqueId = stUniqueId.replace("-","")
	stUniqueId = stUniqueId.replace(" ","")
	return stUniqueId

  def getAudioList(self, exten):  
	print "gettin: " + str(exten)
	result = []
	stRealPath = join(cCONF_BASE_RECORDING(), str(exten))
	stMappedPath = join("/rooms/recordings", str(exten))
	audio = ""
	
	if path.isdir(stRealPath):
		onlyfiles = [ f for f in listdir(stRealPath) if isfile(join(stRealPath,f)) ]
		rowClass = ""
		for f in onlyfiles:
			stFile = stMappedPath + "/" + f
			if rowClass=="rowOdd":
				rowClass="rowEven"
			else:
				rowClass="rowOdd"
			audio += "<tr class='" + rowClass + "'><td valign='middle'><a href='" + stFile + "' alt='Descargar'><img src='tpl/rooms/img/download.png' alt='Descargar pista'></a>&nbsp;<a href='javascript:sendDelRecording(\"" + f + "\");'>&nbsp;<img src='tpl/rooms/img/del.png' alt='Borrar pista'></a>&nbsp;" + f + "<br><br>"
 			audio += ""
			audio += html.format_audio(stFile) + "</td></tr>"
			
	
	return  audio 
				

  
  def render_POST(self, request):
	
	#security check
	usrLogged = get_user(request)
	if not usrLogged:
		return redirectTo("/", request)
		#TODO Inform client to redirect
	
	stUserExten = usrLogged.voip_id

	#prepare to read _POST request
	yRequestArgs = {}
	yRoomArgs = {}
	for a in request.args:		
		yRequestArgs[a] = request.args[a][0]
	
	#Who sends post?
	stActionAMI = yRequestArgs.get('Action', "noAction")
	stAction1 = yRequestArgs.get('hidfrmMyViewAction')
	stAction2 = yRequestArgs.get('hidfrmRoomDataAction')
	stAction3 = yRequestArgs.get('hidfrmTreeAction')
	stAction4 = yRequestArgs.get('hidfrmRoomViewAction')
	
	#AMI EVENTS
	if stActionAMI == "actionuser":
	
		defer = ami.connector.sendAction (yRequestArgs.get('actionAMI'), {"Conference":yRequestArgs.get('conference'), "Channel":yRequestArgs.get('channel')})
		defer.addCallback(self.on_actionOK).addErrback(self.on_actionERR)
		
		return  "Accion en curso" 
	
	elif  stActionAMI == "actionroom":
		
		if yRequestArgs.get('actionAMI') == "ConfbridgeStartRecord":
			
			#Prepare the name of the file that will be recorde. Get unique identifier based on date and time
			#The file will be stored in /var/spool/asterisk/monitor/EXTEN/EXTEN-yyyymmddhhmmss.ogg 
			stUniqueId = self.getUniqueIdFromDate()
			
			stUniqueId = yRequestArgs.get('conference') + "" + stUniqueId + ".ogg"
			stFile = join(yRequestArgs.get('conference'), stUniqueId)
					
			defer = ami.connector.sendAction (yRequestArgs.get('actionAMI'), {"Conference":yRequestArgs.get('conference'), "RecordFile":stFile})			
			defer.addCallback(self.on_actionOKRecording, yRequestArgs.get('conference')).addErrback(self.on_actionERR)
					
			return "Grabando: " + stFile
			 
		elif yRequestArgs.get('actionAMI') == "ConfbridgeStopRecord":

			#Stop recording through ami
			defer = ami.connector.sendAction (yRequestArgs.get('actionAMI'), {"Conference":yRequestArgs.get('conference')})
			defer.addCallback(self.on_actionOKRecording, yRequestArgs.get('conference')).addErrback(self.on_actionERR)	
			
			return ""
			
		else:
			
			#Lock/Unlock
			defer = ami.connector.sendAction (yRequestArgs.get('actionAMI'), {"Conference":yRequestArgs.get('conference')}) 
			defer.addCallback(self.on_actionOK).addErrback(self.on_actionERR)

			return "done: " + yRequestArgs.get('actionAMI')
	
	#MANAGEMENT OF ROOM
	elif  stAction1 == 'EDIT' or stAction1 == 'DEL' or stAction3 == 'SHOW':	
		#ACTION: Load room data in form and display buttons to cancel, commit action

		#set paramsUrl
		if stAction3 == 'SHOW':
			stParamsUrl = '?hidfrmRoomDataAction='+ yRequestArgs['hidfrmTreeAction'] + '&hidIdRoom=' +  yRequestArgs.get('hidfrmTreeIdRoom', -1)
		else:
			stParamsUrl = '?hidfrmRoomDataAction='+ yRequestArgs['hidfrmMyViewAction'] + '&hidIdRoom=' +  yRequestArgs.get('hidfrmMyViewIdRoom', -1)
			
		#skip
		return redirectTo('/rooms' + stParamsUrl, request)

	elif  stAction2 == 'NEWEXEC' or  stAction2 == 'EDITEXEC':
		#ACTION: NEW or EDIT

		nIdRoom = yRequestArgs.get('hidIdRoom', -1)

		#set values
		stUniqueId = self.getUniqueIdFromDate()
			
		yRoomArgs['name'] = yRequestArgs.get('name', 'default' + stUniqueId)
		yRoomArgs['owneruser'] = stUserExten		
		
		#if SelectedItem value is (1:Private)...
		yRoomArgs['secretpin'] = 0
		if int(yRequestArgs.get('cmbVisibility', 1)) == 1:
			#...store pin
			yRoomArgs['secretpin'] = yRequestArgs.get('secretpin', 0)
			
		#manage categories
		yRoomArgs['codCategory'] = yRequestArgs.get('codCategory', 0)

		#call BD
		if yRequestArgs.get('hidfrmRoomDataAction') == 'NEWEXEC':
			nExten = newROOM(yRoomArgs) 
		else:
			#call BD
			nExten = editROOM (nIdRoom, yRoomArgs) 
	
		#skip	
		return redirectTo('/rooms?hidIdRoom=' + nExten, request)

	elif stAction2 == 'DELEXEC':
		#ACTION: DELETE ROOM

		nIdRoom =  yRequestArgs.get('hidIdRoom', -1)
		
		#call BD
		deleteROOM(nIdRoom) 

		#skip
		return redirectTo('/rooms', request)

	elif stAction3 == 'FILTER':
		#ACTION: Filter the view by category

		#set paramsUrl
		stParamsUrl = "?hidfrmTreeAction=FILTER&codCategoryFilterView=" +  yRequestArgs.get("codCategoryFilterView", "-1")
		#skip		
		return redirectTo('/rooms' + stParamsUrl, request)

	elif stAction4== 'DELRECORDING':
		nIdRoom = yRequestArgs.get('hidfrmRoomViewIdRoom', -1)		
		stExten =  str(cCONF_BASE_EXTEN(nIdRoom))
		stFile = yRequestArgs.get('hidfrmRoomViewRecording', -1)		
		stFile = cCONF_BASE_RECORDING() + stExten + "/" + stFile
		if isfile(stFile):
			remove(stFile)
		stParamsUrl = '?hidfrmRoomDataAction=SHOW&hidIdRoom=' +  str(nIdRoom)
		return redirectTo('/rooms' + stParamsUrl, request)
	else:
		#ACTION: READ
		
		#do nothing

		#skip
		return redirectTo('/rooms', request)
		
	
  def render_GET(self, request):
	
	#security check
	usrLogged = session.get_user(request)

	if not usrLogged:
		return redirectTo('/', request)
	
	#interpretation of _GET request
	parts = request.path.split("/")

	if len(parts) > 2 and usrLogged.admin:
		stUserExten = parts[2]
	else:
		stUserExten = usrLogged.voip_id
	
	yRequestArgs = {}
	for a in request.args:
            yRequestArgs[a] = request.args[a][0]
	
		
	#POST 0 managing the recorded files childs accesing by rooms/recordings/room_extension/room_extenyyyymmddhhmmss.ogg
	if len(parts) > 3:			
		if parts[2] == 'recordings':				
			return self.render_recorded_room (request, parts[3], parts[4])
	
	#POST 1 managing categories TODO bring here roomcategories.py  	
	
	
	#POST 2 managing rooms	
	#init display vars	
	ncodCategory = -1
	ncodCategoryFilterView = -1
	
	nFilterTree_Id = -1
	stFilterTree_Type = 'cat'
	
	stName = ''
	nExten = ''
	
	stInfo = ''
		
	cmbPublicVisibility = ''
	cmbPrivateVisibility = ''
	imgPublicVisibility = ''
	imgPrivateVisibility = ''
	secretpindisabled = 'disabled=true'
	nSecretPin = '----'
	listUsersInRoom = ''
	listRecordedFiles = ""
	roomState= ""
	
	idRoom = yRequestArgs.get('idRoom', -1)	
	
	#look for actions to do
	stAction1 =  yRequestArgs.get('hidfrmRoomDataAction', 'READ')
	stAction2 =  yRequestArgs.get('hidfrmMyViewAction', 'READ')
	stAction3 =  yRequestArgs.get('hidfrmTreeAction', 'READ')
	stActionTOSTATE = ""
	if stAction1 in ['DEL', 'EDIT', 'SHOW']: 
		#ACTION: fill the form with existing data

		#fetch data		
		idRoom = yRequestArgs.get('hidIdRoom')
    		regRoom = getROOM(idRoom)
		yLineasR = ''
		
		#fill display vars
		for xroom in regRoom:
			stName = xroom.name
			ncodCategory = xroom.codCategory
			
			#tree
			nFilterTree_Id  = cCONF_BASE_EXTEN(xroom.idRoom)
			stFilterTree_Type = 'room'	
		
			#visibilty				
			if xroom.secretpin == 0:
				imgPublicVisibility = '<img src="/tpl/rooms/img/roomVoid.png">'
				cmbPublicVisibility  = 'selected'
				secretpindisabled = ' disabled=true '	
				nSecretPin = "----"			
			else:
				imgPrivateVisibility = '<img src="/tpl/rooms/img/roomPrivate.png">'
				cmbPrivateVisibility = 'selected'
				secretpindisabled = ''
				nSecretPin = xroom.secretpin
			
			#ask CLI for users already in room
			listUsersInRoom = getConfbridgeStatusListOfUsersForInputSelect(cCONF_BASE_EXTEN(xroom.idRoom))
			
			#List of recordings in room directory 
			listRecordedFiles = self.getAudioList(cCONF_BASE_EXTEN(xroom.idRoom))

			yResult = getConfbridgeStatus() 
			if yResult.has_key(nExten):
				roomState =  yResult[str(cCONF_BASE_EXTEN(xroom.idRoom))][1]
			else:
				roomState = "unlocked"

		#specific del or edit settings		
		if stAction1 == 'DEL':
			stInfo = ''
			stActionTOSTATE = "DELEXEC"			
			
		elif stAction1 == 'EDIT':
			stInfo = ''
			stActionTOSTATE = "EDITEXEC"			
						
		elif stAction1 == 'SHOW':
			stInfo = ''
			stActionTOSTATE = "SHOW"			
			
	elif stAction3 == 'FILTER':
		
		ncodCategoryFilterView = yRequestArgs.get('codCategoryFilterView', 'READ')
			
		nFilterTree_Id = yRequestArgs.get('codCategoryFilterView', 'READ')
		stFilterTree_Type = 'cat'
		
		stActionTOSTATE = "FILTER"
		
	else:

		stActionTOSTATE = "READ" 
		
		#After saving selection or record
		nFilterTree_Id = yRequestArgs.get('hidIdRoom', -1)
		stFilterTree_Type = 'room'	
	
	#load array to echo data
	yRoomArgs = { 'idRoom':idRoom, 'RoomExtension': nFilterTree_Id, 'RoomName': stName, 'cmbPrivateVisibility':cmbPrivateVisibility, 'cmbPublicVisibility':cmbPublicVisibility,  'imgPrivateVisibility':imgPrivateVisibility, 'imgPublicVisibility':imgPublicVisibility, 'stSecretPinDisabled':secretpindisabled, 'nSecretPin': nSecretPin, 'listCATEG': getROOMCATEGORIES(ncodCategory), 'listCATEGVIEW': getROOMCATEGORIES (ncodCategoryFilterView), 'myViewROOMS':  getROOMS (stUserExten, ncodCategoryFilterView), 'info': stInfo, 'treeUL': getROOMCATEGORIEStree(stUserExten), 'codFilterTreeId': nFilterTree_Id, 'codFilterTreeType': stFilterTree_Type, 'ActionTOSTATE':stActionTOSTATE, 'listUsersInRoom': listUsersInRoom, "listRecordedFiles":listRecordedFiles, "roomState":roomState}
	
	#call rooms.html file through content-pbx-lorea	
	content = print_template('rooms/rooms-front', yRoomArgs)
	return print_template('content-pbx-lorea', {'content': content})

  def getChild(self, name, request):
	return self
 
  def render_recorded_room(self, request, exten, recordedFile):
	
	request.setHeader('Content-Description', 'File Transfer')
	request.setHeader('Content-Type', 'application/octet-stream')
	request.setHeader('Content-Disposition', 'attachment; filename='+recordedFile)
	request.setHeader('Content-Transfer-Encoding', 'binary')
	request.setHeader('Cache-Control', 'no-cache, must-revalidate') # http1.1
	request.setHeader('Pragma', 'no-cache') # http1.0
	
	with open(cCONF_BASE_RECORDING() + exten + "/" + recordedFile) as f:
		request.setHeader('Content-Length', f)
		return f.read()


