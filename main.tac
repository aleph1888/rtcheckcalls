from twisted.web import server
from twisted.internet import reactor
from twisted.application import service, strports
from obelisk.resources.root import RootResource
from obelisk import daemon

# Create the root resource
toplevel = RootResource()

# Hooks for twistd
application = service.Application('Voip Manager')
server = strports.service('tcp:8080', server.Site(toplevel))
server.setServiceParent(application)
daemon.run()
