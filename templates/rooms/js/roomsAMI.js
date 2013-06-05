//monitoring AMI EVENTS js functions-->

		function execAMIactionUsr(nAction){
		
			var elSel = document.getElementById('lstUsers');	
			if (elSel.selectedIndex == -1) {return}		
			
			var stChannel = $('option:selected', $("#lstUsers")).attr('channel');
			var nConference = getSelectedNodeId();
			 			
   			$.post("rooms", {"Action":"actionuser", "actionAMI": nAction, "conference":nConference, "channel":stChannel}, function(data){
   			 		
   				 });
		}

		function execAMIactionRoom(nAction){
			
			
			var nConference = getSelectedNodeId();
			
   			$.post("rooms", {"Action":"actionroom", "actionAMI": nAction, "conference":nConference}, function(data){
   			 		
   				 });
		}
		
			
		function execAMIactionRoomLock(){

			if (document.getElementById("botRoomLock").roomState == "locked"){
				stAction = "ConfbridgeUnlock";
			}else{
				stAction = "ConfbridgeLock";
			}
			var nConference = getSelectedNodeId();
			
   			$.post("rooms", {"Action":"actionroom", "actionAMI": stAction, "conference":nConference}, function(data){
   			 
   				 });
		}
		
		function execAMIactionRoomRec(){
		
			if (document.getElementById('botRoomRec').recordingState=="ON"){				
				stAction = "ConfbridgeStopRecord"}
			else{
				stAction = "ConfbridgeStartRecord";
			}
	
					
			var nConference = getSelectedNodeId();
			$.post("rooms", {"Action":"actionroom", "actionAMI": stAction, "conference":nConference}, function(data){
   			 		
   			});
		}
		
		
		/*
		function muteUnmute(){
			
			var actionToDo = document.getElementById('botRoomUserMute').value;
			
			if ( actionToDo =="Mute")
				{actionToDo="Unmute"}else{actionToDo="Mute"}
				
			document.getElementById('botRoomUserMute').value = actionToDo
			execAMIactionUsr('Confbridge' + actionToDo);
		}*/
		

		function initializeAMI() {

			if (!!window.EventSource) {
				var source = new EventSource('/sse');
		
			} else {
				console.log('no registra');
		  		// Result to xhr polling :(
			}

			function setInfo (stText) {
				document.getElementById("txtEvents").value = document.getElementById("txtEvents").value + "\n" + stText;
			}

			//{"privilege": "call,all", "conference": "9077", "event": "ConfbridgeStart"}
			source.addEventListener('bridge_start', function(e) {
				setInfo(e.data);
				console.log(e.data);
				var data = JSON.parse(e.data);
				
				//VIEW actions
				document.getElementById("imgStarted" + data.conference).src = "/tpl/rooms/img/roomON.png";
				
				//TREE actions
				selectInTree(data.conference, "room");
				changeIco (data.conference, "ON");
				
				setRoomButtons();
				
			}, false);
			
			function manageINOutRoom(e){

					setInfo(e.data);
					console.log(e.data);
					var data = JSON.parse(e.data);			
					console.log(data);
								
					var nNumUsers = 0
				
					//DATA actions
					//get and clear selecdt
					/*var elSel = document.getElementById('lstUsers');				
					elSel.length = 0;*/	
				
					//fill with options
					for (user in data.usersInRoom) {
	 				 	 				 	
		 				/*var elOptNew = document.createElement('option');
						elOptNew.text = data.usersInRoom[user];
						elOptNew.value = 'user' + user;
						elOptNew.setAttribute('channel', data.channel);
						elSel.add(elOptNew);*/
					
						nNumUsers++;
					}
				
					$("#tdNumUsers" + data.conference).text(nNumUsers);
				
					//TREE actions
					selectInTree(data.conference, "room");
					stNodeText = " [" + String(nNumUsers) + "]"
					console.log(stNodeText);
					renameNode(stNodeText, data.conference, "room", true);
					setUserButtons();
				}	

			//{"conference": "9077", "calleridnum": "6008", "usersInRoom": {"9999":"9999:name", "9998":"name2"}", calleridname": "aleph", "uniqueid": "1361405344.424", calleridname": "aleph", "calleridname": "aleph", "privilege": "call,all", "event": "ConfbridgeJoin", "channel": "SIP/aleph-000000a6"}
			source.addEventListener('bridge_join', function(e) {
				manageINOutRoom(e);
			}, false);

			//{"conference": "9077", "calleridnum": "6008",   "usersInRoom": {"9999":"9999:name", "9998":"name2"}", "uniqueid": "1361405344.424",  calleridname": "aleph", "privilege": "call,all", "event": "ConfbridgeLeave", "channel": "SIP/aleph-000000a6"}
			source.addEventListener('bridge_leave', function(e) {					
				//do nothing
			}, false);

			//{"privilege": "call,all", "conference": "9077", "event": "ConfbridgeEnd"}
			source.addEventListener('bridge_end', function(e) {

				manageINOutRoom(e);

				setInfo(e.data);
				console.log(e.data);
				var data = JSON.parse(e.data);
				

				//VIEW actions
				document.getElementById("imgStarted" + data.conference).src = "/tpl/rooms/img/roomVoid.png";
				
				//TREE actions
				stNodeText = "";
				selectInTree(data.conference, "room");
				renameNode(stNodeText, data.conference, "room")
				changeIco (data.conference, "OFF");
				
				setRoomButtons();
				
			}, false);
			
			source.addEventListener('on_action', function(e) {
				var jobj = JSON.parse(e.data);
				data = jobj.info;
				
				console.log(data.message);
				switch (data.message) {
					case "User muted":
						document.getElementById("botRoomUserMute").value = "Desmutear";
						document.getElementById("botRoomUserMute").onclick = function(e){execAMIactionUsr('ConfbridgeUnmute');};
						break;
					case "User unmuted":
						document.getElementById("botRoomUserMute").value = "Mutear";
						document.getElementById("botRoomUserMute").onclick = function(e){execAMIactionUsr('ConfbridgeMute');};
						break;
					case "Conference Recording Started.":	
						document.getElementById("botRoomRec").value = "Parar grabación";
						document.getElementById("botRoomRec").recordingState = "ON";	
						document.getElementById("recInfo").innerHTML = "<img src='tpl/rooms/img/recordingON.gif'width=28>&nbsp;Grabando...";
						break;
					case "Conference Recording Stopped.":	
						document.getElementById("botRoomRec").value = "Iniciar grabación";
						document.getElementById("botRoomRec").recordingState = "OFF";
						document.getElementById("recInfo").innerHTML = "<img src='tpl/rooms/img/recordingOFF.gif' width=26>&nbsp;Las grabaciones ocupan espacio en el servidor. Graba con responsabilidad.";
						document.getElementById("tdRecordedList").innerHTML = jobj.audiolist;
						break;
					case "Conference is already being recorded.":
						document.getElementById("botRoomRec").value = "Parar grabación";
						document.getElementById("botRoomRec").recordingState = "ON";	
						document.getElementById("recInfo").innerHTML  = "<img src='tpl/rooms/img/recordingON.gif' width=28>&nbsp;¡La grabación ya estaba en marcha!";
						break;
					case "Internal error while stopping recording." || "Conference is already being recorded.":
			 			$.post("rooms", {"Action":"actionroom", "actionAMI": "ConfbridgeStopRecord", "conference":nConference}, function(data){
	   			 		//document.getElementById("tdRecordedList").innerHTML = data;
	   					});
						break;
					case "Conference locked":
						document.getElementById("botRoomLock").value = "Desbloquear Sala";	
						document.getElementById("botRoomLock").roomState = "locked";	
						break;
					case "Conference unlocked":	
						document.getElementById("botRoomLock").value = "Bloquear Sala";
						document.getElementById("botRoomLock").roomState = "unlocked";
						break;
					case "No Channel by that name found in Conference.":
						//todo resolve conflict regenerating user list.						
						alert('pagina desfasda');
						break;
					}

				
				setInfo(data);
				console.log(data);			
			}, false);
			
			//{"privilege": "call,all", "conference": "9077", "event": "ConfbridgeEnd"}
			source.addEventListener('bridge_talking', function(e) {
				setInfo(e.data);
				console.log(e.data);
			}, false);
		}


