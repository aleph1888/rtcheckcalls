import subprocess
from twisted.internet import reactor
from decimal import Decimal
import math

from obelisk.accounting import accounting
from obelisk import calls

filename = "/var/log/asterisk/cel-custom/Master.csv"

class CallMonitor(object):
    def __init__(self, id, cost, app_from, app_to):
	    self._id = id
	    self._callID = 0
            self._provider = 'unknown'
            if cost:
		    self._realcost = Decimal(cost)
	    else:
		    self._realcost = Decimal()
	    try:
		    self._cost = Decimal(cost)
		    if self._cost:
			    self._cost += Decimal(0.001) # benefit margin
	    except:
		    self._cost = Decimal(0.0)
	    self._from = app_from
	    self._to = app_to
    def on_app_start(self, args):
	    self._starttime = 0
            provider = args[10].split("/")
	    if len(provider) > 2:
		provider = provider[1]
	    else:
		provider = 'direct'
            self._provider = provider
	    print "call from %s to %s with %s mana remaining (%s)" % (self._from, self._to, accounting.get_mana(self._from), self._provider)
    def on_answer(self, args):
	    print "check %s answered %s on channel %s" % (args[3], args[6], args[8])
	    if self._from == args[3] and self._to == args[5]:
		    channel = args[8]
		    print "%s answered on channel %s" % (self._from, channel)
		    self._starttime = float(args[0])
		    self._channel = channel
		    self.predict_cut()
		    #reactor.callLater(10, self.cut_call, channel)
    def predict_cut(self):
	    if not self._cost:
		    print "free call, will not be cut"
		    return
	    mana = accounting.get_mana(self._from)
	    if not mana:
		    self.cut_call(self._channel, "not enough credit for call")
	    else:
		    time_to_cut = (float(mana) / float(self._cost)) * 60.0
		    print "CUT IN %s" %(time_to_cut)
		    self._callID = reactor.callLater(int(time_to_cut), self.cut_call, self._channel, "out of credit while calling")
    def cut_call(self, channel, reason=""):
	    self._callID = 0
	    if reason:
		    print "CUTTING CALL (%s)" % (reason, )
	    else:
		    print "CUTTING CALL"
            print self.run_asterisk_cmd("channel request hangup %s" % (channel))
    def on_chan_start(self, args):
	    channel = args[8]
	    # precut call if user can't pay it
	    if self._cost and not accounting.get_mana(self._from):
		    self.cut_call(channel, "not enough credit")
    def on_hangup(self, args):
	    if self._callID:
		    self._callID.cancel()
		    self._callID = 0
	    endtime = float(args[0])
	    if self._starttime:
	    	    totaltime = endtime - self._starttime
		    self.apply_costs(totaltime)
		    print "call end %.1f seconds at %s per minute" % (totaltime, self._cost)
            else:
		    print "unsuccesfull call"
    def apply_costs(self, totaltime):
	    if self._from in accounting.get_data():
		    # round up to closest second
		    totaltime = math.ceil(totaltime)
		    # round up to closest minute
		    roundedtime = totaltime
		    if totaltime % 60:
			    roundedtime += 60 - (totaltime % 60)
	            minutes = roundedtime / 60
	            # calculate total cost
		    totalcost = self._cost * Decimal(minutes)
		    # add call establishment
		    if self._cost:
			    totalcost += Decimal('0.001')
		    # save accounting data
		    accounting.remove_credit(self._from, totalcost)
                    calls.add_call(self._from, self._to, self._starttime, totaltime, roundedtime, totalcost, self._cost, self._provider)

    def run_asterisk_cmd(self, cmd):
	    return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])

    def run_command(self, cmd):
	    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	    return output

class CallManager(object):
    def __init__(self):
	self._commands = {}
	self._commands["HANGUP"] = self.on_hangup
	self._commands["CHAN_START"] = self.on_chan_start
	self._commands["APP_START"] = self.on_app_start
	self._commands["CHAN_END"] = self.on_chan_end
	self._commands["ANSWER"] = self.on_answer
	self._commands["BRIDGE_START"] = self.on_bridge_start
	self._commands["BRIDGE_END"] = self.on_bridge_end
	self._calls = {}
    def write(self, text):
	#print text
	pass
    def on_text(self, text):
	parts = text.split(",")
	parts = map(lambda s: s.strip('"'), parts)
	command = parts[0]
	id = parts[-7]
	if command in self._commands:
	    self._commands[command](parts[1:])
	else:
	    self.write("? " + command + " " + str(parts[1:]))
    def on_chan_start(self, args):
	    app_uniqid = args[14]
	    if app_uniqid in self._calls:
		    self._calls[app_uniqid].on_chan_start(args)
	    self.write("chan start: " +  str(args) + " " + str(args[14]))
    def on_app_start(self, args):
	    app_from = args[3]
	    app_to = args[5]
	    app_uniqid = args[14]
	    app_cost = args[-7]
	    self.write("app start: " + app_from + " " + app_to + " " + str(args[14]) + " " + str(args))
	    if not app_uniqid in self._calls:
		    self._calls[app_uniqid] = CallMonitor(app_uniqid, app_cost, app_from, app_to)
		    self._calls[app_uniqid].on_app_start(args)
    def on_chan_end(self, args):
	    self.write("chan end: " +  str(args) + " " + str(args[14]))
    def on_hangup(self, args):
	    app_uniqid = args[14]
	    if app_uniqid in self._calls:
		    self._calls[app_uniqid].on_hangup(args)
		    del self._calls[app_uniqid]
	    self.write("hangup: " + " " + str(args) + " " + str(args[14]))
    def on_answer(self, args):
	    app_uniqid = args[14]
	    if app_uniqid in self._calls:
		    self._calls[app_uniqid].on_answer(args)
	    self.write("answer: " + str(args) + " " + args[14])
    def on_bridge_start(self, args):
	    self.write("bridge start: " +  str(args) + " " + str(args[14]))
    def on_bridge_end(self, args):
	    self.write("bridge end: " +  str(args) + " " + str(args[14]))

if __name__ == '__main__':
	from tail import tail
	from time import sleep
	m = CallManager()
	
	m.on_text('"HANGUP","1354410942.161893","","701","","","","","from-payuser","SIP/1.0.0.9-00000001","AppDial","(Outgoing Line)","3","0.0","1354410928.1","1354410928.0","","","","16,SIP/1.0.0.9-00000001,"')
	
	t = tail(filename, m.on_text)
	while True:
		t.process()
		sleep(1)


