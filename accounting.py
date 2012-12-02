from twisted.internet import reactor
import json
import os

class Accounting(object):
	def __init__(self):
		self.load_data()

	def load_data(self):
		if os.path.exists("accounts.json"):
			f = open("accounts.json", "r")
			data = f.read()
			f.close()
			self._data = json.loads(data)
		else:
			self._data = {}
			self.save_data()
		self.save_data()

	def save_data(self):
		f = open("accounts.json", "w")
		f.write(json.dumps(self._data))
		f.close()
		f2 = open("accounts2.json", "w")
		f2.write(json.dumps(self._data))
		f2.close()

	def get_mana(self, user):
		if user in self._data:
			return self._data[user]
		else:
			return 0.0

	def add_credit(self, user, credit):
		if user in self._data:
			self._data[user] += credit
		else:
			self._data[user] = credit
		self.save_data()

accounting = Accounting()
