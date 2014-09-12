#!/usr/bin/python

import sys

#ofil = open(datetime.datetime.today().strftime("csk_%y%m%d%H%M.wpl").'w')

for pline in sys.stdin:
	try:
        	line = pline.split('HEX ')[1]
		#ofil.write(line)
		print(line),
	except:
		exit()
