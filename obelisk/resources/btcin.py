import json
import os
import json

from decimal import Decimal

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

from obelisk.resources import sse

from obelisk.model import Model, User, Wallet

from obelisk.tools.cypher import check_signature
from obelisk.config import config


class BtcInResource(Resource):
    def __init__(self):
        Resource.__init__(self)

    def render_POST(self, request):
        signed_data = request.args['data'][0]
        if not 'fingerprint' in config:
            return 'daemon not configured'
        result = check_signature(signed_data, config['fingerprint'])
        if result:
            json_data, timestamp = result
        else:
            return "invalid signature"
        data = json.loads(json_data)
        address = data['address']
        balance = data['balance2']
        balance_confirmed = data['balance']
        timestamp = data['timestamp']
        self.apply_transaction(address, balance, balance_confirmed, timestamp)
        return "ok"

    def apply_transaction(self, address, balance, balance_confirmed, timestamp):
        model = Model()
        wallet = model.query(Wallet).filter_by(address=address).first()
        if wallet and wallet.user:
            user = wallet.user
            balance_unconfirmed = Decimal(balance) / Decimal("100000000")
            balance_confirmed = Decimal(balance_confirmed) / Decimal("100000000")
            received = wallet.received
            if not wallet.received:
                received = Decimal("0")
            new_coins = balance_confirmed - received

            wallet.received = balance_confirmed
            wallet.unconfirmed = balance_unconfirmed

            # XXX need to add a mechanism to account credit (convert to euros)
            #user.credit += new_coins
            print "applied transaction", balance_confirmed, balance_unconfirmed, user, user.voip_id
            model.session.commit()
            sse.resource.notify(
                {'confirmed': float(balance_confirmed), 'unconfirmed': float(balance_unconfirmed), 'currency': 'BTC'},
                'balance', user)
        else:
            print "unknown tx destination"

    def getChild(self, name, request):
        return self

