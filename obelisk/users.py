from obelisk.asterisk.users import create_user as create_asterisk_user
from obelisk.kamailio.users import create_user as create_kamailio_user
from obelisk.kamailio.users import create_alias
from obelisk.kamailio.model import session, KamailioUser
from obelisk.model import Model

from obelisk.config import config

def create_user(username, password):
	# create user for asterisk
	peer = create_asterisk_user(username, password)
	if not peer:
		return False

	# now, also create user in kamailio if configured
	if config.get('kamailio', False):
		create_kamailio_user(username, password)
		create_alias(username, peer.regexten)

		# we take the password kamailio has and put it into the obelisk table
		# so when or if kamailio is using asterisk db it will find it there)
		model = Model()
		user = session.query(KamailioUser).filter_by(username=username).first()
		peer.sippasswd = user.ha1
		model.session.commit()
	
	return peer

