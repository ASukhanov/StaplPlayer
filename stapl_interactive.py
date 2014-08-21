# Interactive wrapper for StaplPlayer
# Version 2	2014-08-20
# Example of a session of shifting in 3 numbers into IR$10 and IR$12 :
#i10
#1
#2
#3
#x	#execute the list
#x	#repeat the list
#n	#reset the list, start new one
#i12
#1
#2
#3
#x

import subprocess

irscan_lines = ''
drscan_lines = ''

while 1:
  s=raw_input('')
  if len(s) == 0:
      exit()
  elif s[0] == 'x':
    f = open('stapl.stp','w')
    f.write('ACTION	TRANS = DO_TRANS;\n')
    f.write('DATA PARAMETERS;\n')
    f.write('BOOLEAN idcode_data[32*10];\n')
    f.write('BOOLEAN irdata[10*32];\n')
    f.write('ENDDATA;\n')

    f.write('PROCEDURE DO_TRANS USES PARAMETERS;\n')
    f.write('IRSTOP IRPAUSE;\n')
    f.write('DRSTOP DRPAUSE;\n')
    f.write(irscan_lines)
    f.write(drscan_lines)
    f.write('ENDPROC;\n')
    f.close()
    
    #print("Stapl instructions:\n")
    #f = open('stapl.stp','r')
    #for s in f:
    #  print(s),
    #f.close()
    # execute action
    p = subprocess.Popen('StaplPlayer -aTRANS stapl.stp', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
      print line,
      retval = p.wait()
  elif s[0] == 'i':
    irscan_lines += 'IRSCAN 8, $' + s[1:] + ', CAPTURE irdata[7..0];\n'
  elif s[0] == 'n':	#reset command list
    irscan_lines = ''
    drscan_lines = ''
  else:  
    drscan_lines += 'STATE IDLE;\n'
    drscan_lines += 'DRSCAN 32, $' + s + ', CAPTURE idcode_data[31..0];\n'
    drscan_lines += 'EXPORT "Shifted Out:", idcode_data[31..0];\n'
