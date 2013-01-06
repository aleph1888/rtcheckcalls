from twisted.web import server
from twisted.internet import reactor
from twisted.application import service, strports
from root_resource import RootResource
import daemon

# Create the root resource
toplevel = RootResource()

# Hooks for twistd
application = service.Application('Voip Manager')
server = strports.service('tcp:8080', server.Site(toplevel))
server.setServiceParent(application)
daemon.run()
