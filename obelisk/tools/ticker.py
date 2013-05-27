import json
import urllib2
from twisted.internet import reactor
import traceback
import random

price = 50.0
mins = 30

def from_mtgox():
    u = urllib2.urlopen('http://data.mtgox.com/api/1/BTCEUR/ticker')
    data = json.loads(u.read())
    u.close()
    return data

def parse_results(data):
    if data['result'] == 'success':
        values = data['return']
        return float(values['buy']['value'])
      
def ticker_thread():
    global price
    print "start thread"
    try:
        data = from_mtgox()
        price = parse_results(data)
    except:
        # call each 
        print "Problems on ticker"
        traceback.print_exc()
    # mins to mins*2 minutes
    reactor.callLater(60*mins+random.randint(0, 60*mins), ticker)
    print "end thread", price

def ticker():
    reactor.callInThread(ticker_thread)

if __name__ == '__main__':
    reactor.callLater(5, ticker)
    reactor.run()

