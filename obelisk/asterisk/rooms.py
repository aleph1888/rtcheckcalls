from obelisk.asterisk.model import SipPeer, Extension
from obelisk.asterisk import cli
from obelisk.model import Model, Room, Rooms_categories

from datetime import *

def cCONF_BASE_RECORDING():
	return "/var/spool/asterisk/monitor/"

def cCONF_BASE_EXTEN(nIdRoom):
	return 9000 + int(nIdRoom)

#ROOMS VIEW: gets <tr></tr> of row ROOMS {All my rooms UNION All public rooms}
#TDs: [edit and delete buttons][name][extension][public/private][started]*[num users in room]* ----- *to do, read from CLI
def getROOMS(stOwnerUser, nCodCategoryFilter):
	 
	model = Model()
	
	#fetch data
	
	if str(nCodCategoryFilter) != "-1":
		#if there's a Category filter
		regRoomsMy = model.query(Room.idRoom, Room.name, Room.owneruser, Rooms_categories.categoryname, Room.secretpin, Room.codCategory).filter(Room.owneruser==stOwnerUser, Room.codCategory==nCodCategoryFilter).join(Rooms_categories)
	else:
		#get all records
		regRoomsMy = model.query(Room.idRoom, Room.name, Room.owneruser, Rooms_categories.categoryname, Room.secretpin).filter(Room.owneruser==stOwnerUser).join(Rooms_categories)
		 

	#fill return var with lines
	yConfStatus = getConfbridgeStatus()
	yReturn = ''
	cRowAlternating = "rowOdd"
	for xroom in regRoomsMy:
		nExten =  str(cCONF_BASE_EXTEN(xroom.idRoom))
		
		#mount columns
		
		if xroom.owneruser == stOwnerUser:
			stEditLink = '<td><a href=javascript:sendEdit(' + str(xroom.idRoom) + ');><img src="tpl/rooms/img/edit.png" alt="Editar"></a>'
			stDelLink = '<a href=javascript:sendDel(' + str(xroom.idRoom) + ');><img src="tpl/rooms/img/del.png" alt="Borrar"></a></td>'
		else:
			stEditLink = '<td>-'
			stDelLink = '-</td>'
			
		stInfoFields = '<td>'+ xroom.name + '</td><td>' + str(cCONF_BASE_EXTEN(xroom.idRoom))+ '</td><td>'+xroom.categoryname + '</td>'
		
		bPublic = (xroom.secretpin==0)
		if bPublic:
			bPublic = '<img id="imgVisibility' + nExten + '" name="imgVisibility' + nExten + '" src="tpl/rooms/img/roomVoid.png" alt="Las salas privadas requieren c&oacute;digo PIN.">'
		else:
			bPublic = '<img id="imgVisibility' + nExten + '" name="imgVisibility' + nExten + '" src="tpl/rooms/img/roomPrivate.png" alt="Las salas privadas requieren c&oacute;digo PIN.">'
			
		stVisibility = '<td>' + bPublic + '</td>'
		
		if yConfStatus.has_key(nExten):
			stStarted = '<img id="imgStarted' + nExten + '" name="imgStarted' + nExten + '" src="tpl/rooms/img/roomON.png" alt="Las salas privadas requieren c&oacute;digo PIN.">'
			nUsers = str(yConfStatus[nExten][0])
			stLocked = '<img id="imgLocked' + nExten + '" name="imgLocked' + nExten + '" src="tpl/rooms/img/roomLocked.png" alt="Estado de acceso a la sala">'
		else:
			stStarted = '<img id="imgStarted' + nExten + '" name="imgStarted' + nExten + '" src="tpl/rooms/img/roomVoid.png" alt="">'			
			nUsers = "0"
			stLocked = '<img id="imgLocked' + nExten + '" name="imgLocked' + nExten + '" src="tpl/rooms/img/roomVoid.png" alt="Estado de acceso a la sala">'

		stStarted = '<td>' + stStarted + '</td>'
		stNumUsrs = '<td id="tdNumUsers' + nExten + '">' + nUsers + '</td>'
		stLocked = '<td>' + stLocked + '</td>'
						
			
		#table row	
		if cRowAlternating=="rowOdd":
			cRowAlternating="rowEven"
		else:
			cRowAlternating="rowOdd"
					
		yReturn = yReturn + '<tr class="'+ cRowAlternating + '">' + stEditLink + stDelLink + stInfoFields + stVisibility + stStarted + stNumUsrs + '</tr>'
		
		
	return yReturn

def getROOM (nIdRoom):
	
	model = Model()
	return model.query(Room.idRoom, Room.name, Room.codCategory, Room.secretpin, Rooms_categories.categoryname).filter_by(idRoom=nIdRoom).join(Rooms_categories)
		
#CATEGORIES: gets the option list for html select	
def getROOMCATEGORIES(nSelectedCategory):
	 
	model = Model()
	regRoomCategories = model.query(Rooms_categories)

	yReturn = ''  
	for xroomCategory in regRoomCategories:
		if (nSelectedCategory != -1) and (xroomCategory.idCategory == int(nSelectedCategory)):
			stSelected = "selected"
		else:
			stSelected = ""
		yReturn = yReturn + '<option ' + stSelected + ' value="' + str(xroomCategory.idCategory) + '">'+ xroomCategory.categoryname + '</option>'	
	
	return yReturn
	
def getConfbridgeStatusListOfUsersForInputSelect(nExten):
	#TODO.... column MENU ??????
	
	#OUTPUT
	#
	#Channel                       User Profile     Bridge Profile   Menu             CallerID
	#============================= ================ ================ ================ ================
	#SIP/aleph-000000c0            default_user     default_bridge                    6008             

	
	#yUsers = "#Channel                       User Profile     Bridge Profile   Menu             CallerID\n"
	#yUsers +="============================= ================ ================ ================ ================\n"
	#yUsers +="SIP/aleph-000000c0            default_user     default_bridge                    6008\n"
		
	#run command
	yUsers = cli.run_command("confbridge list " + str(nExten))
	
	#Cut by lines
	yUsers = str(yUsers).split("\n")[2:]

	#SepyRoomsarar campos	
	yResult = ""
	
	if len(yUsers) > 0:		
		for line in yUsers:						
			line = line.split()			
			if len(line)>0:				
				stCallerId =  line[len(line)-1]
				stCallerExten = line[len(line)-1] + ':' + str(line[0]).replace("SIP/","").split("-")[0]	
				stCallerChannel	= line[0]
				yResult = yResult + '<option  channel="' + stCallerChannel + '" value="user' + stCallerId + '">' + stCallerExten  + '</option>'
				
	
	return yResult	

def getConfbridgeStatusDictionaryOfUsersInRoom(nExten):
	
	#OUTPUT
	#
	#Channel                       User Profile     Bridge Profile   Menu             CallerID
	#============================= ================ ================ ================ ================
	#SIP/aleph-000000c0            default_user     default_bridge                    6008             

	#run command
	yUsers = cli.run_command("confbridge list " + str(nExten))
	
	#Cut by lines deprecating first and second.
	yUsers = str(yUsers).split("\n")[2:]
	
	#For each line, extract user information
		
	yResult = {}	
	if len(yUsers) > 0:		 
		for line in yUsers:				
			line = line.split()			
			if len(line)>0:
				yResult[line[3]] = line[3] + ':' + str(line[0]).replace("SIP/","").split("-")[0]
	
	return yResult

#Returns a dictionary of active rooms with values (numusers, locked)
def getConfbridgeStatus():
	
	#OUTPUT
	#	Conference Bridge Name           Users  Marked Locked?
	#	================================ ====== ====== ========
	#	9087                                  1      0 unlocked
	#	9087                                  1      0 unlocked

	#run command
	yRooms = cli.run_command("confbridge list")
	nNumFields = 4 

	#Cut by lines
	yRooms = str(yRooms).split("\n")[2:]

	#Cut empty element
	
	yRooms = yRooms[:1]
	
	#SepyRoomsarar campos	
	yResult = {}
	if len(yRooms) > 0:
		for line in yRooms:	
			line = line.split()
			if len(line)>0:
				yResult[line[0]] = (line[1], line[3])

	#yResult dictionary of{name, users}
	return yResult
	
#CATEGORY TREE MANAGEMENT: gets all childs of a category as --> <ul><li id="li9999"> <a>categoryname</a><ul>{CHILDS}</ul></li></ul>
def getROOMCATEGORYnode (nIdCategory, stUser, yConfStatus):
	
	model = Model()
	xCategories = model.query(Rooms_categories).filter_by(codCategoryParent=nIdCategory)

	if xCategories:
		yReturn = '<ul>'  
		for xroomCategory in xCategories:
			yReturn = yReturn + '<li rel="category" id="cat' + str(xroomCategory.idCategory) + '" name="cat' + str(xroomCategory.idCategory) + '"><a>' + str(xroomCategory.categoryname) + '</a>'   
			yReturn = yReturn + getROOMSofCATEGORYnode (xroomCategory.idCategory, stUser, yConfStatus)
			yReturn = yReturn + getROOMCATEGORYnode (xroomCategory.idCategory, stUser, yConfStatus)
			yReturn = yReturn +  '</li>'
		yReturn = yReturn + '</ul>'  	
	
	return yReturn
	


#CATEGORY TREE MANAGEMENT: gets all ROOMS of a category as --> <ul><li id="roomEXTENSION"><a>room name</a></li></ul>
def getROOMSofCATEGORYnode (nIdCategory, stUser, yConfStatus):
	
	model = Model()
	regRooms = model.query(Room).filter_by(codCategory=nIdCategory)
	if regRooms:
		yReturn = '<ul>'
		for xRoom in regRooms:
			nExten =  str(cCONF_BASE_EXTEN(xRoom.idRoom))
			if (stUser == xRoom.owneruser):
				stEditable = " edit=true " 
			else:
				stEditable = " edit=false "
			
			if yConfStatus.has_key(nExten):
				stroomStarted = "ON"
				stNumUsers = " [" + yConfStatus[nExten][0] + "]"
				stRoomState = yConfStatus[nExten][1]
			else:
				stroomStarted = "OFF"
				stNumUsers = "[0]"	
				stRoomState = "locked"
				
			yReturn = yReturn + '<li rel="room' + stroomStarted  + '" roomState="' + stRoomState + '" roomStarted="' + stroomStarted + '" ' + stEditable + 'roomName="' +  xRoom.name + '" id="room' + nExten + '" name="room' + nExten + '"><a>' + str(xRoom.name) + ' [' + str(cCONF_BASE_EXTEN(xRoom.idRoom)) + ']' + stNumUsers+ '</a>'   
			yReturn = yReturn +  '</li>'
		yReturn = yReturn + '</ul>'  	
	 
	return yReturn

#CATEGORY TREE MANAGEMENT: gets <ul></ul> tree of categories
def getROOMCATEGORIEStree(stUser):
	yConfStatus = getConfbridgeStatus()
	return getROOMCATEGORYnode (0, stUser, yConfStatus)

def newROOM (yRoomArgs):
	
	model = Model()

	#check name disponibiliy; change if repited name
	if model.query(Room).filter_by(name=yRoomArgs['name']).first():
		yRoomArgs['name'] = yRoomArgs['name'] + str(datetime.today())[0:9];
	
	#create room in database
	room = create_room_internal(model,
			name=yRoomArgs['name'],
			bridge=2,
			owneruser=yRoomArgs['owneruser'],
			secretpin= yRoomArgs['secretpin'],
			codCategory=yRoomArgs['codCategory']
			
	)

	return str(cCONF_BASE_EXTEN(room.idRoom))
	
def newCATEGORY (stCategoryName, ncodCategoryParent):
	
	model = Model()
	#Fetch existing or...
	if model.query(Rooms_categories).filter_by(categoryname=stCategoryName).first():
		Rooms_Category = model.query(Rooms_categories).filter_by(categoryname=stCategoryName)		
		return Rooms_Category.idCategory
	else:
		#... create new room_category 
		Rooms_Category = create_room_category_internal(model, categoryname=stCategoryName, codCategoryParent = ncodCategoryParent)
		return Rooms_Category.idCategory


def create_room_internal(model, **kwargs):
	room = Room (**kwargs)
	model.session.add(room)
	model.session.commit()
	add_extension(str(cCONF_BASE_EXTEN(room.idRoom)), room.secretpin)	
	return room
		

def create_room_category_internal(model, **kwargs):
	Rooms_Category = Rooms_categories (**kwargs)
	model.session.add(Rooms_Category)
	model.session.commit()
	
	return Rooms_Category

def add_extension(extension, secretpin):
	model = Model()
	nPrioridad = 1	
	new_extensionASW = Extension('to-rooms', extension, nPrioridad, 'Answer','')
	model.session.add(new_extensionASW)
	
	nPrioridad = nPrioridad + 1
	if secretpin != 0:
		new_extensionSET = Extension('to-rooms', extension, nPrioridad, 'set', 'CONFBRIDGE(user,pin)=' + str(secretpin))
		model.session.add(new_extensionSET)
		nPrioridad = nPrioridad + 1 	
	
	new_extensionBRIDGE = Extension('to-rooms', extension, nPrioridad, 'ConfBridge', extension)
	model.session.add(new_extensionBRIDGE)
	model.session.commit()
	
def editROOM (nIdRoom, yRoomArgs):
	
	model = Model()

	#fetch data
	xRoom = model.query(Room).filter_by(idRoom=nIdRoom).first()
	if not xRoom:
		return str(cCONF_BASE_EXTEN(nIdRoom))
	
	#set values
	xRoom.name=yRoomArgs['name']	
	xRoom.owneruser=yRoomArgs['owneruser']
	xRoom.secretpin= yRoomArgs['secretpin']
	xRoom.codCategory=yRoomArgs['codCategory']
	
	#del and recreate extension, todo: could edit only if changed
	nExten =  cCONF_BASE_EXTEN (nIdRoom)
	model.query(Extension).filter_by(exten=nExten).delete()
	add_extension(nExten, xRoom.secretpin)
	
	model.session.commit()	
	return str(cCONF_BASE_EXTEN(nIdRoom))

def deleteROOM(nIdRoom):

	model = Model()

	#eliminar extension
	nExten =  cCONF_BASE_EXTEN(nIdRoom)
	model.query(Extension).filter_by(exten=nExten).delete()
	
	#eliminar room		
	model.query(Room).filter_by(idRoom=nIdRoom).delete()
	model.session.commit()

	return True

    
