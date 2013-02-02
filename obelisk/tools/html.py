def format_table(results):
	output = "<table>\n"
	for idx, result in enumerate(results):
		output += "<tr><td>"
		output += "</td><td>".join(result)
		output += "</td></tr>\n"
	output += "</table>\n"
	return output

def format_audio(source):
	output = "<audio controls>\n"
	output += "  <source preload='none' src='%s' type='audio/ogg'>\n" % (source,)
	output += "</audio>\n"
	return output

