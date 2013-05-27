import json
import urllib2
from twisted.internet import reactor
from twisted.web.client import getPage

import traceback
import random

price = 50.0
mins = 30

def from_mtgox():
    d = getPage('http://data.mtgox.com/api/1/BTCEUR/ticker')
    return d

def parse_results(data):
    if data['result'] == 'success':
        values = data['return']
        return float(values['buy']['value'])

def wait_and_tick(err=None):
   reactor.callLater(60*mins+random.randint(0, 60*mins), ticker)
     
def ticker_update(data):
    global price
    data = json.loads(data)
    price = parse_results(data)
    print "ticker update", price

def ticker():
    global price
    try:
        d = from_mtgox()
        d.addCallback(ticker_update)
        d.addCallback(wait_and_tick)
        d.addErrback(wait_and_tick)
    except:
        # call each 
        print "Problems on ticker"
        traceback.print_exc()
        wait_and_tick()

if __name__ == '__main__':
    ticker()
    reactor.run()

