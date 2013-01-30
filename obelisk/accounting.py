from twisted.internet import reactor
import os
from decimal import Decimal

from obelisk import charges
from obelisk.model import Model, User
from obelisk.resources import sse
from obelisk.asterisk.model import SipPeer

class Accounting(object):
	def __init__(self):
		self.model = Model()

	def get_data(self):
		data = {}
		users = self.model.query(User)
		for user in users:
			data[user.voip_id] = user.credit
		return data

	def get_mana(self, user_ext):
		user = self.model.get_user_fromext(user_ext)
		if user:
			return user.credit
		else:
			return Decimal()

	def reset_credit(self, user_ext):
		user = self.model.get_user_fromext(user_ext)
		user.credit = Decimal()
		self.model.session.commit()

	def transfer_credit(self, logged, user_ext, credit):
		if not (credit > 0.0 and logged.credit >= credit):
			return
		user = self.model.get_user_fromext(user_ext)
		if not user:
			# check at least user exists as asterisk user
			peer = self.model.query(SipPeer).filter_by(regexten=user_ext).first()
			if not peer:
				return
			user = User(user_ext)
			self.model.session.add(user)
		logged.credit -= Decimal(credit)
		user.credit += Decimal(credit)
		self.model.session.commit()
		charges.add_charge(user_ext, credit, 'transferencia de ' + logged.voip_id)
		charges.add_charge(logged.voip_id, -credit, 'transferencia a ' + user_ext)
		sse.resource.notify({'credit': float(user.credit), 'user': user.voip_id}, "credit", user)
		sse.resource.notify({'credit': float(logged.credit), 'user': logged.voip_id}, "credit", logged)
	
	def add_credit(self, user_ext, credit):
		user = self.model.get_user_fromext(user_ext)
		if not user:
			user = User(user_ext)
			self.model.session.add(user)
		user.credit += Decimal(credit)
		self.model.session.commit()
		charges.add_charge(user_ext, credit)
		sse.resource.notify({'credit':float(user.credit), 'user':user.voip_id}, "credit", user)

	def remove_credit(self, user_ext, credit):
		user = self.model.get_user_fromext(user_ext)
		if not user:
			return

		user.credit -= Decimal(credit)
		self.model.session.commit()

accounting = Accounting()

if __name__ == '__main__':
	print accounting.get_data()
	print accounting.get_mana('816')
	accounting.reset_credit('816')
	accounting.add_credit('816', 1.949000)
	print accounting.get_mana('816')
	accounting.remove_credit('816', 1.0)
	print accounting.get_mana('816')
