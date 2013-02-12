import os
import time

# sanity checks
if not os.path.exists("/etc/asterisk/providers.conf"):
	print "providers file doesnt exist"

starttime = time.time()
