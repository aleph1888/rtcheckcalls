from twisted.internet import reactor
import os
from decimal import Decimal

from obelisk import charges
from obelisk.model import Model, User

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
		
	def add_credit(self, user_ext, credit):
		user = self.model.get_user_fromext(user_ext)
		if not user:
			user = User(user_ext)
			self.model.session.add(user)
		user.credit += Decimal(credit)
		self.model.session.commit()
		charges.add_charge(user_ext, credit)

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
