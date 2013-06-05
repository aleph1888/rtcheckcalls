//tree section-->
	
	function initializeTree(nInitiallySelected){
	
		//Subscribe to loaded event of the tree to select the current item		    
		$("#myjsTree").bind('loaded.jstree', on_myjstree_loaded);
		//Suscribe to select_node room
		$("#myjsTree").bind('select_node.jstree', on_myjstree_select_node);
	
		//CREATE TREE
		$('#myjsTree').jstree({ 
					"types" : {
					    "valid_children" : [ "room" ],
					    "themes" : {
						"theme" : "default",
						"dots" : true,
						"icons" : true
						},
					    "types" : {
						"category" : {
						    "icon" : { 
							"image" : "/tpl/rooms/img/category.png" 
						    },
						},
						"roomOFF" : {
						    "icon" : { 
							"image" : "/tpl/rooms/img/roomOFF.png" 
						    },
						},
						"roomON" : {
						    "icon" : { 
							"image" : "/tpl/rooms/img/roomON.png" 
						    },
						},
						
						"default" : {
						    "valid_children" : [ "default" ]
						}
					    }
					},
					"ui" : {
						"select_limit" : 1,
						"initially_select" : ["#" + nInitiallySelected]						
						},
					"plugins" : ["themes","html_data","dnd","ui","types"]
					
				    });
	
		}

	
	
   	
    	//EDIT or DEL buttons for each record of the view
	function sendShow (nIdRoom)  {
	
		document.getElementById("hidfrmTreeIdRoom").value = nIdRoom;
		document.getElementById("hidfrmTreeAction").value = 'SHOW';
		
		document.getElementById("frmTree").action = "/rooms";			
		document.getElementById("frmTree").submit();		
	}
	
	function sendShowTree() {
    		sendShow(parseInt($("#myjsTree").jstree("get_selected").attr("id").split("room")[1]) - 9000);    				
    	}
		
    	function sendEditTree() {
    		sendEdit(parseInt($("#myjsTree").jstree("get_selected").attr("id").split("room")[1]) - 9000);    				
    	}
    	
    	function getSelectedNodeId(){    	 
    		if  (typeof  $("#myjsTree").jstree("get_selected") === "undefined"){
    			return -1;}
    		else{
    			return  $("#myjsTree").jstree("get_selected").attr("id").split("room")[1];}
    	}
    	
    	function sendDelTree() {
    		sendDel(parseInt( $("#myjsTree").jstree("get_selected").attr("id").split("room")[1]) - 9000);      	
    	}
    	
    	//SELECT PRESENT category
	function selectInTree(nId, stCATorROOM ) {	
		$("#myjsTree").jstree("deselect_all");
		if (String(nId) != "-1") { 		
			stFromIDToNODE = '#' + stCATorROOM + String(nId);
			$.jstree._reference(stFromIDToNODE).open_node(stFromIDToNODE);
			$.jstree._reference(stFromIDToNODE).select_node(stFromIDToNODE);		
		}
	}
	
	function renameNode (stNewText, nExten, stCATorROOM, bADDatEND){
		stFromIDToNODE = '#' + stCATorROOM + String(nExten);
		stReturnText = $.jstree._reference(stFromIDToNODE)._get_node(stFromIDToNODE).attr("roomName"); 
		stReturnText = stReturnText + ' [' + $.jstree._reference(stFromIDToNODE)._get_node(stFromIDToNODE).attr("id").replace("room","")  + ']';
		
		if (bADDatEND) {		
			stReturnText = stReturnText + stNewText;			
		}
				
		$.jstree._reference(stFromIDToNODE).rename_node(stFromIDToNODE, stReturnText);
		$.jstree._reference(stFromIDToNODE).select_node(stFromIDToNODE);
	}
	
	function changeIco(nExten, stOFForON) {
		
		stFromIDToNODE = '#room' + String(nExten);
		$.jstree._reference(stFromIDToNODE)._get_node(stFromIDToNODE).attr("roomStarted", stOFForON);
		$.jstree._reference(stFromIDToNODE)._get_node(stFromIDToNODE).attr("rel", "room" + stOFForON);
	
}
	
	function isSelectedRoomStarted(){				
		console.log("is" + bIsStarted);
		return bIsStarted;
	}

	function isSelectedRoomLocked(){	
		if  (typeof  $("#myjsTree").jstree("get_selected").attr("roomState")  === "undefined"){
    			return false;}
    		else{
    			var stSelected = $("#myjsTree").jstree("get_selected").attr("roomState")
			return stSelected == "locked";
		}	
	}
	
    	//Subscribe to loaded event of the tree to select the current item		
    	function on_myjstree_loaded (event, data){    		
		$("#myjsTree").jstree("open_all")
    		//NOTICE: there is a call to INITIALLY_SELECT on jstree() call
		document.getElementById("divTree").style.display = "inline";	
		//Initialization made by TREE_select_node. Reset state in order that new selections could be done
		 stActionTOstate = initializeData(stActionTOstate);	
		console.log(stActionTOstate);
		setRoomButtons();
    	}
    	
    	    	
    	//Suscribe to click on room
    	function on_myjstree_select_node (event, data){    				
	    		console.log("lista");
	    	if (stActionTOstate=="SHOW"){
	    		stActionTOstate = initializeData('SHOW');

	    	}
	    	if (stActionTOstate=="READ"){
  			//Hide, show buttons --> if category:none;room:all --> if private room of other user:none
	    		bIsRoom = String(data.rslt.obj.attr("id")).split("room")[0]=="";
	    		bIsEditable = ("true" == String(data.rslt.obj.attr("edit")));

	    		if (bIsRoom && bIsEditable){initializeData('ROOM')}
	    		else{initializeData('CATEGORY')}
	    	}	
	    	else{
	    		stActionTOstate ="READ";	    		
	    	}    
		bIsStarted = $("#myjsTree").jstree("get_selected").attr("roomStarted") == "ON";	    		
		console.log("lista" + bIsStarted);	
		setRoomButtons ();	
    	}
    	
    
	function sendNewRoomCategory()  {		

		if ($("#txtNewCategory").val() == "")
			{document.getElementById("infoarea").innerHTML ="Introduce un nombre categoría";}
		else{
			if  (typeof  $("#myjsTree").jstree("get_selected") === "undefined" || typeof  $("#myjsTree").jstree("get_selected").attr("id") === "undefined"){
	    			document.getElementById("infoarea").innerHTML = "Selecciona una categoría en el árbol";}
	    		else{
	    			if ($("#myjsTree").jstree("get_selected").attr("id").split("cat").length!=2)
					{document.getElementById("infoarea").innerHTML = "Selecciona una categoría en el árbol, no una sala.";}
				else {
					document.getElementById("hidfrmTreeCodCategory").value = $("#myjsTree").jstree("get_selected").attr("id").split("cat")[1]; 						document.getElementById("hidfrmTreeAction").value = 'NEWEXEC';
					document.getElementById("frmTree").action = "/roomscategory";
					document.getElementById("frmTree").submit();	
				}
			}
		}
	}		
	
	
	
