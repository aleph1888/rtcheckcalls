import subprocess
from obelisk.resources import sse

class TestChannels(object):
    def run_asterisk_cmd(self, cmd):
            return self.run_command(['/usr/sbin/asterisk', '-nrx', cmd])

    def run_command(self, cmd):
            output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            return output

    def get_channelstats(self):
	raw_data = self.run_asterisk_cmd("sip show channelstats")
	raw_data = raw_data.split("\n")[1:-2]
	#print raw_data
	data = {}
	for line in raw_data:
		peer = line[:18].strip()
		call_id = line[18:31].strip()[:10]
		duration = line[31:40].strip()
		rx_pack = line[40:52].strip()
		rx_lost = line[52:63].strip()
		rx_per = line[63:72].strip(" )(")
		rx_jitter = line[72:79].strip()
		tx_pack = line[79:91].strip()
		tx_lost = line[91:102].strip()
		tx_per = line[102:111].strip(" )(")
		tx_jitter = line[111:].strip()
		#print peer, call_id, rx_per, tx_per
		data[call_id] = [call_id, duration, rx_pack, rx_lost, rx_per, rx_jitter, tx_pack, tx_lost, tx_per, tx_jitter]
	return data

    def get_channels(self):
	raw_data = self.run_asterisk_cmd("sip show channels")
	raw_data = raw_data.split("\n")[1:-2]
	#print raw_data
	data = {}
	for line in raw_data:
		peer = line[:18].strip()
		user = line[18:35].strip()
		call_id = line[35:52].strip()[:10]
		format = line[52:69].strip()
		hold = line[69:78].strip()
		last_message = line[78:94].strip()
		expiry = line[94:105].strip()
		peer_name = line[105:].strip()
		if not 'nothing' in format:
			#print "%s/"*8 % (peer, user, call_id, format, hold, last_message, expiry, peer_name)
			data[call_id] = [peer, user, call_id, format, hold, last_message, expiry, peer_name]
	return data

    def get_rates(self):
	rates = []
	channels = self.get_channels()
	stats = self.get_channelstats()
	for channel in channels:
		if channel in stats:
			c = channels[channel]
			s = stats[channel]
			# print c[0], c[1], c[3], s[2:6], s[6:10]
			rates.append({'ip': c[0], 'name': c[1], 'format': c[3], 'rx': s[2:6], 'tx': s[6:10]})
	return rates



if __name__ == '__main__':
	t = TestChannels()
	print t.get_rates()

