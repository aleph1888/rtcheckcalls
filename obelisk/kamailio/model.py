from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Sequence, Numeric, DateTime, Float, ForeignKey, Text, Boolean

from obelisk.config import config

session = None
if 'kamailio' in config:
    cfg = config['kamailio']
    db = create_engine('mysql://%s:%s@%s/%s' % (cfg['user'],
						cfg['password'],
						cfg.get('host', 'localhost'),
						cfg['database']))
    DBSession = sessionmaker(db)
    session = DBSession()

class KamailioUser(Base):
	__tablename__ = 'subscriber'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	username = Column(String(64))
	domain = Column(String(64))
	email_address = Column(String(64))
	ha1 = Column(String(64))
	ha1b = Column(String(64))

	def __repr__(self):
		return "<KamailioUser('%s', '%s')>" % (self.username, self.domain)

if __name__ == '__main__':
	m = session.query(KamailioUser).filter_by(username='caedes')
	for a in m:
		print a
