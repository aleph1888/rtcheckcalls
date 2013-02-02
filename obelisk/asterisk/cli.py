import subprocess

def run_command(command):
	return subprocess.Popen(['/usr/sbin/asterisk', '-nrx', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
