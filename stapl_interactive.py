#!/usr/bin/python
# Interactive wrapper for StaplPlayer
# Version 3	2014-08-22
#
# Example of a session:
#i10 20 30 40 #comment1
#'this line will be added for execution
#40 50 #comment2 60 70

import subprocess
import string

outLines = ''
print('Enter list of commands (p to play the list):')
while 1:
  l=raw_input('')
  if len(l) == 0:
     continue
  if l[0] == 'p':	# build the stapl file /run/shm/stapl.stp and play it
    f = open('/run/shm/stapl.stp','w')
    f.write('ACTION	TRANS = DO_TRANS;\n')
    f.write('DATA PARAMETERS;\n')
    f.write('BOOLEAN idcode_data[32*10];\n')
    f.write('BOOLEAN irdata[10*32];\n')
    f.write('INTEGER ii;\n')
    f.write('ENDDATA;\n')
    
    f.write('PROCEDURE DO_TRANS USES PARAMETERS;\n')
    f.write(outLines)
    f.write('ENDPROC;\n')
    f.close()
    
    #print("Stapl instructions:\n")
    #f = open('/run/shm/stapl.stp','r')
    #for s in f:
    #  print(s),
    #  f.close()
    
    # execute action
    line = 'StaplPlayer -aTRANS /run/shm/stapl.stp'
    print('Executing "'+line+'"');
    p = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
      if line[0:6] == 'Export':
        print(line.split('HEX ')[1]),
      #print line,
      retval = p.wait()
    continue

  if l[0] == 'x':
    exit()
  if l[0] == 'n':   # reset command list
    print('List reset')
    outLines = ''
  if l[0] == '\'':
    outLines += l[1:] + '\n'
    continue

  for s in l.split():
    #s.lstrip('>')
    if s[0] == '#':	# comment
      break
    elif s[0] == 'i':	# IRSCAN instruction
      outLines += 'IRSCAN 8, $' + s[1:] + ', CAPTURE irdata[7..0];\n'
    elif s[0] == 'n':	# reset command list
      outLines = ''
    elif all(c in string.hexdigits for c in s):	# DRSCAN instruction
      outLines += 'DRSCAN 32, $' + s.rjust(8,'0') + ', CAPTURE idcode_data[31..0];\n'
      outLines += 'EXPORT "Shifted Out:", idcode_data[31..0];\n'
    else:
      print('Unknown token: '+s)
