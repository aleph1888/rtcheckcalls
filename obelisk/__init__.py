# sanity checks
import os
if not os.path.exists("/etc/asterisk/providers.conf"):
	print "providers file doesnt exist"
