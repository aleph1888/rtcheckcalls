def format_table(results, attributes={}):
	if 'class' in attributes:
		output = "<table class='%s'>\n" % (attributes['class'], )
	else:
		output = "<table>\n"
	for idx, result in enumerate(results):
		if idx % 2:
			css = 'even'
		else:
			css = 'odd'
		if idx == 0:
			td = 'th'
		else:
			td = 'td'
		output += "  <tr class='%s'>\n    <%s>" % (css, td)
		td_split = "</%s>\n    <%s>" % (td, td)
		output += td_split.join(result)
		output += "</%s>\n  </tr>\n" % (td, )
	output += "</table>\n"
	return output

def format_audio(source):
	output = "<audio controls>\n"
	output += "  <source preload='none' src='%s' type='audio/ogg'>\n" % (source,)
	output += "</audio>\n"
	return output

