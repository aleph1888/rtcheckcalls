sel = 0;
function load_calls(user_ext, start, end) {
	var ncol = start/10;
	//$('#accounting_tbody').fadeOut(200);
	$.get('/user/json/'+user_ext+"/"+start+"/"+(end-start), type='json', callback=function(data, textStatus) {
		var text = ''
		if (typeof(data) == "string") {
			alert('error... tal vez haya caducado tu sesion?')
		}
		else {
			$('#accounting_'+sel).attr('class', '');
			$('#accounting_'+ncol).attr('class', 'row_selected');
			sel = ncol;
			for(var idx=0; idx<data.length; idx++)
			{
				var col = data[idx];
				text += '<tr>';
				for(var cdx=0; cdx<col.length; cdx++) {
					var c = col[cdx];
					text += '<td>'+c+'</td>';
				}			
				text += '</tr>';
			}

			$('#accounting_tbody').html(text) // .fadeIn()
		}
	})
}
