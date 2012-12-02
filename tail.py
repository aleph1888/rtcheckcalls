#!/usr/bin/env python

'''A module which implements a unix-like "tail" of a file.
A callback is made for every new line found in the file.  Options
specify whether the existing contents of the file should be read
or ignored.

@author Sean Reifschneider <jafo@tummy.com>
@version $Revision: 1.52 $

Released under the GPLv2 or any later version.

If a file is emptied or removed, the tail will continue reading lines
which are written in the new place.

Simple example:

	import tail

	def callback(line):
		print 'Line: "%s"' % string.rstrip(line)

	tail.tail('/var/log/all', callback).mainloop()
'''

import time
import string
import os

class tail:
	def __init__(self, filename, callback, tailbytes = 0):
		'''Create a new tail instance.
		Create a tail object which periodicly polls the specified file looking
		for new data which was written.  The callback routine is called for each
		new line found in the file.

		@return Nothing
		@param filename File to read.
		@param callback Function which takes one argument, called with each
				line read from the file.
		@param tailbytes Specifies bytes from end of file to start reading
				(defaults to 0, meaning skip entire file, -1 means read full file).
		'''
		self.skip = tailbytes
		self.filename = filename
		self.callback = callback
		self.fp = None
		self.lastSize = 0
		self.lastInode = -1
		self.data = ''

	def process(self):
		'''Examine file looking for new lines.
		When called, this function will process all lines in the file being
		tailed, detect the original file being renamed or reopened, etc...
		This should be called periodicly to look for activity on the file.

		@return Nothing
		'''
		#  open file if it's not already open
		if not self.fp:
			try:
				self.fp = open(self.filename, 'r')
				stat = os.stat(self.filename)
				self.lastIno = stat[1]
				if self.skip >= 0 and stat[6] > self.skip:
					self.fp.seek(0 - (self.skip), 2)
				self.skip = -1
				self.lastSize = 0
			except:
				if self.fp: self.fp.close()
				self.skip = -1    #  if the file doesn't exist, we don't skip
				self.fp = None
		if not self.fp: return

		#  check to see if file has moved under us
		try:
			stat = os.stat(self.filename)
			thisSize = stat[6]
			thisIno = stat[1]
			if thisSize < self.lastSize or thisIno != self.lastIno:
				raise Exception
		except:
			self.fp.close()
			self.fp = None
			self.data = ''
			return

		#  read if size has changed
		if self.lastSize < thisSize:
			while 1:
				thisData = self.fp.read(4096)
				if len(thisData) < 1:
					break
				self.data = self.data + thisData

				#  process lines within the data
				while 1:
					pos = string.find(self.data, '\n')
					if pos < 0: break
					line = self.data[:pos]
					self.data = self.data[pos + 1:]
					#  line is line read from file
					if self.callback: self.callback(line)

		self.lastSize = thisSize
		self.lastIno = thisIno

	def mainloop(self, sleepfor = 5):
		'''Loop forever processing activity on the tail object.
		This routine is intended to be called in programs which do not need
		to do other processing.  This routine never returns.

		@return Never returns
		@param sleepfor Seconds between processing (default is 5 seconds).
		'''
		while 1:
			self.process()
			time.sleep(sleepfor)

if __name__ == "__main__":
	def callback(line):
		print 'Line: "%s"' % string.rstrip(line)

	tail('/var/log/all', callback).mainloop()
