from obelisk.kamailio.kamctl import kamctl
from obelisk.config import config

def create_user(username, password):
	kamctl('add %s %s' % (username, password))

def create_alias(username, alias):
	domain = config['domain']
	kamctl('alias_db add %s %s' % (alias + '@' + domain, username + '@' + domain))

