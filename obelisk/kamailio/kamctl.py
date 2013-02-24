import subprocess

def kamctl(cmd):
	return subprocess.Popen(['/usr/sbin/kamctl']+cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

if __name__ == '__main__':
	print kamctl('uptime')
