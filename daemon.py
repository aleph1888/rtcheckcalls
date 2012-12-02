from tail import tail
from twisted.internet import reactor
from rtcheckcalls import CallManager

filename = "/var/log/asterisk/cel-custom/Master.csv"

m = CallManager()
t  = tail(filename, m.on_text)


def loop():
        t.process()
	reactor.callLater(1, loop)

def run():
	reactor.callLater(1, loop)

if __name__ == '__main__':
	reactor.run()
