#!/usr/bin/python

# Logic analyzer display of the 'StaplPlayer -aTRANS chipskop.stp'

import sys
from matplotlib.widgets import Cursor
#import numpy as np
import matplotlib.pyplot as plt
import subprocess
import datetime

#ofname = '/run/shm/' + datetime.datetime.today().strftime("csk_%y%m%d%H%M.wpl")
ofname = '/tmp/' + datetime.datetime.today().strftime("csk_%y%m%d%H%M.wpl")
ofile  = open(ofname,'w')

valnum = 0
values = list()
for i in range(0,16+1):
        values.append(list())

def mybin(val): # convert integer to 16 binary digits
        rc = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
        ibit = 1
        for ii in range (0,16):
                if val & ibit !=0 :
                        rc[ii] = 1
                ibit = ibit << 1
        return rc

def process_line(pline,split):
	global valnum
	if split:
	  #print(pline),
          if pline[0:6] != 'Export':
                return
          line = pline.split('HEX ')[1]
	  ofile.write(line)
	  pline = line
        value = pline.split()
        for i in range(0, len(value)):
                values[0].append(valnum)
                valnum = valnum+1
                binbits = mybin(int(value[i],16))
                for ii in range(0, len(binbits)):
                        values[ii+1].append(str(float(binbits[ii])*.5+ii))
	return

if(len(sys.argv)>1):
  print('Opening '+sys.argv[1])
  sfil = open(sys.argv[1],'r')
  title = sys.argv[1]
  for pline in sfil:
	process_line(pline,0)
else:
  title = datetime.datetime.today().strftime("csk_%y%m%d%H%M.wpl")
  line = 'StaplPlayer -aTRANS chipskop.stp'
  print('Executing "'+line+'"');
  p = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for pline in p.stdout.readlines():
	process_line(pline,1)
print('Hex waveform is written to ' + ofname)
fig = plt.figure(figsize=(16, 8))
fig.suptitle(title,fontsize=12)
fig.subplots_adjust(left=0.02)
fig.subplots_adjust(right=0.98)
fig.subplots_adjust(bottom=0.05)
fig.subplots_adjust(top=0.98)
ax = fig.add_subplot(111, axisbg='#FFFFCC')

#print 'len(values)=',len(values)
#print 'values[0]=',values[0]
#print 'values[4]=',values[4]

for i in range(1, len(values)):
	try:
		ax.plot(values[0], values[i], '-')
	except:
		break

cursor = Cursor(ax, useblit=True, color='red', linewidth=2 )
 
plt.show()
