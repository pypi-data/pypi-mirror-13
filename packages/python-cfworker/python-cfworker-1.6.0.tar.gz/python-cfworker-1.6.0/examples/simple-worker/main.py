#!/usr/bin/python

import os, time
from cfworker import cfworker

cfworker().start()

while True:
	print 'working...'
	time.sleep(2)
