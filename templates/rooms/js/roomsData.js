//global

	function hideEveryThing (){

		document.getElementById('hidfrmTreeEditButton').style.display = 'none';
		document.getElementById('hidfrmTreeDelButton').style.display = 'none';
		document.getElementById('hidfrmTreeNewButton').style.display = 'none';
		
		document.getElementById('hidfrmTreeShowButton').style.display = 'none';
		
		document.getElementById('divRoomData').style.display = 'none';
		document.getElementById('divRoomView').style.display = 'none';
		document.getElementById('secViews').style.display = 'none';
	
		document.getElementById('EDITSaveButtons').style.display = 'none';
		document.getElementById('DELSaveButtons').style.display = 'none';
		document.getElementById('NEWSaveButtons').style.display = 'none';
		
	}

	function initializeData (stSTATE){
			
		hideEveryThing();
		
		if (stSTATE=='DELEXEC'){
			
			document.getElementById('divRoomData').style.display = 'inline';
			document.getElementById('DELSaveButtons').style.display = 'inline';
		}

		if (stSTATE=='EDITEXEC'){
			
			document.getElementById('divRoomData').style.display = 'inline';
			document.getElementById('EDITSaveButtons').style.display = 'inline';
		}

		if (stSTATE=='NEW'){
			document.getElementById('divRoomData').style.display = 'inline';			
			document.getElementById('NEWSaveButtons').style.display = 'inline';			
					
			//to do: EMPTY FIELDS
			document.getElementById('name').value="";
			document.getElementById('secretpin').value="----";
			document.getElementById('cmbVisibility').selectedIndex = 0;

		}

		if(stSTATE=='SHOW'){
			document.getElementById('divRoomView').style.display = 'inline';		
			
			document.getElementById('hidfrmTreeEditButton').style.display = 'inline';
			document.getElementById('hidfrmTreeDelButton').style.display = 'inline';
			document.getElementById('hidfrmTreeNewButton').style.display = 'inline';
			setUserButtons();
			setRoomButtons();
			return 'SHOWED';	
		}
		
		if (stSTATE=='FILTER'){
			document.getElementById('hidfrmTreeNewButton').style.display = 'inline';
			document.getElementById('secViews').style.display = 'inline';
		}

		if (stSTATE=='READ'){
			document.getElementById('hidfrmTreeNewButton').style.display = 'inline';
			document.getElementById('secViews').style.display = 'inline';
		}

		if (stSTATE=='ROOM'){
			document.getElementById('hidfrmTreeNewButton').style.display = 'inline';
			document.getElementById('hidfrmTreeShowButton').style.display = 'inline';
			document.getElementById('secViews').style.display = 'inline';

		}

		if (stSTATE=='CATEGORY'){
			document.getElementById('hidfrmTreeNewButton').style.display = 'inline';
			document.getElementById('secViews').style.display = 'inline';
		}
			
		return stSTATE;
	}

//frMViewData------------------------------
	function setUserButtons () {	
		
		var elSel = document.getElementById('lstUsers');
		
		$("#botRoomUserKick")[0].disabled = elSel.selectedIndex == -1;
		$("#botRoomUserMute")[0].disabled = elSel.selectedIndex == -1;
		
		
	}
	
	function setRoomButtons () {	
		
		var bRoomStarted = isSelectedRoomStarted();
 		console.log(">>>>" + bRoomStarted);			
		$("#botRoomRec")[0].disabled = !bRoomStarted;
		$("#botRoomLock")[0].disabled = !bRoomStarted;
				
		
		if (bRoomStarted) 
		{	
						
			var bRoomLocked = isSelectedRoomLocked();
			
			console.log(bRoomLocked);
			if (bRoomLocked){
				document.getElementById("botRoomLock").value = "Desbloquear Sala";
			}else{
				document.getElementById("botRoomLock").value = "Bloquear Sala";
			}
		}		
	}

	function sendDelRecording(stFile)
	{
		if(confirm("¿Deseas eliminar " + stFile + "?")){
			document.getElementById("hidfrmRoomViewAction").value= 'DELRECORDING';
			document.getElementById("hidfrmRoomViewRecording").value= stFile;
			document.getElementById("frmRoomView").submit();
		}

	}

//frmRoomData	--------------------------------
	//SECRETPIN, numeric validation
	function isNumeric (f) {
		
		if (isNaN(f.value)) {
			console.log("Error:\nEste campo debe tener sólo números.");
			f.focus();
			return (false);
		 }
	}

	//VIBILITY, public or private changing: {0 Public; 1 Private}
	function visibilityChangingUI () {			
		
		document.getElementById('secretpin').disabled = document.getElementById('cmbVisibility').value == 0;
		if (!document.getElementById('secretpin').disabled) {
			document.getElementById('secretpin').value = "1234"
		}else
		{	document.getElementById('secretpin').value = "----"}
		
		document.getElementById('secretpin').focus();								
	}

	//CATEGORIES. Predefined options in category select: 
			// {0 / Choose category}
			// {1 / New category} To add new category to BD, choose item in frmRoomData.codCategory 
	function categoryChangingUI (callerObj) {
						
		bAddNewCategory = (callerObj.id == "txtNewCategory") || (document.getElementById("codCategory").selectedIndex == 1);
		document.getElementById("txtNewCategory").disabled = !bAddNewCategory;
		if (bAddNewCategory){
			document.getElementById("codCategory").selectedIndex = 1;
			document.getElementById("txtNewCategory").value = "";
			document.getElementById("txtNewCategory").focus();			
		} else {
			document.getElementById("txtNewCategory").value = "Crea CATEGORÍA";
		}
	}	
	
	// Delete and Edit buttons events. Check frmRoomData.hidfrmRoomDataAction value to catch current action:
	/*	
		EDIT, DEL					reload page to set values in frmRoomData and commit/cancel buttons.
		EDITEXEC, DELEXEC, NEWEXEC			calls BD 
		FILTER						reload page, filtering, view
	*/
	function NewDelEditButtons (idRoom, stAccion)  {							
		
		if (stAccion == 'READ'){
			stActionTOstate = initializeData('SHOW'); 

		}else{
			document.getElementById("hidfrmRoomDataAction").value = stAccion;
			document.getElementById("hidIdRoom").value = idRoom;
			document.getElementById("frmRoomData").submit();
		};
	}
		

//frmMyView----------------------------
	
	//CATEGORIES. Submit to filtering the view
		// {-1 / All categories}
	function CategoryFilterSubmit (codCategory)  {			
		document.getElementById("hidfrmTreeAction").value = 'FILTER';
		document.getElementById("frmTree").submit();
	}	


	//EDIT or DEL buttons for each record of the view
	function sendEdit(idRoom)  {		
		document.getElementById("hidfrmMyViewAction").value = 'EDIT';
		document.getElementById("hidfrmMyViewIdRoom").value = idRoom;
		document.getElementById("frmMyView").submit();		
	}
			 
	function sendDel(idRoom)  {
		document.getElementById("hidfrmMyViewAction").value = 'DEL';
		document.getElementById("hidfrmMyViewIdRoom").value = idRoom;
		document.getElementById("frmMyView").submit();	
	}



