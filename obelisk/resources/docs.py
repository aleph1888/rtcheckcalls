from twisted.web.resource import Resource


from obelisk.templates import print_template

class DocsResource(Resource):
    def render_GET(self, request):
	parts = request.path.split("/")
	if len(parts) == 2:
		parts.append('contents')
	if len(parts) > 2:
		section = parts[2]
		try:
			content = print_template('docs/' + section, {})
		except:
			content = "la seccion no existe"
		return print_template("content-pbx-lorea", {'content': content})
    def getChild(self, name, request):
        return self
