# Wrapper for StaplPlayer

import sys
if len(sys.argv) < 2:
  print('No arguments\n Usage example : staplcmd i8 1 2 i10 deadface fe0dfe0f')
  print('will do:\nIRSCAN $8; DRSCAN 32 $1; DRSCAN 32 $2;')
  print('IRSCAN $10;  DRSCAN 32 $deadface; DRSCAN 32 $fe0dfe0f;')
  exit()

f = open('stapl.stp','w')
f.write('ACTION	TRANS = DO_TRANS;\n')
f.write('DATA PARAMETERS;\n')
f.write('BOOLEAN idcode_data[32*10];\n')
f.write('BOOLEAN irdata[10*32];\n')
f.write('ENDDATA;\n')

f.write('PROCEDURE DO_TRANS USES PARAMETERS;\n')
f.write('IRSTOP IRPAUSE;\n')
f.write('DRSTOP DRPAUSE;\n')
for s in sys.argv[1:]:
  if s[0] == 'i':
    f.write('IRSCAN 8, $' + s[1:] + ', CAPTURE irdata[7..0];\n')
    f.write('WAIT IDLE, 1 CYCLES;\n')
  else:
    f.write('DRSCAN 32, $' + s + ', CAPTURE idcode_data[31..0];\n')
    f.write('EXPORT "Shifted Out:", idcode_data[31..0];\n')
f.write('ENDPROC;\n')
f.close()

#print("Stapl instructions:\n")
#f = open('stapl.stp','r')
#for s in f:
#  print(s),
#f.close()

# execute action
import subprocess
p = subprocess.Popen('StaplPlayer -aTRANS stapl.stp', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
  print line,
retval = p.wait()
