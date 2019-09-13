#!/usr/bin/python
# Wrapper for StaplPlayer
# Packs program arguments into a STAPL file stapl.stp and plays it using StaplPlayer
# Version 3	2014-10-21
# Version 4     2016-02-19. Using environment variables.  
# Version v5	2016-04-01. sp_option_passthrough comes from -o option to work with XU2 command port
__version__ = 'v06 20190912' #do not crash when nonstartdard options are not used.
import sys
import os
try:
    gpio_jtag0_cs = int(os.environ['GPIO_JTAG0_CS'])
    gpio_jtag1_cs = int(os.environ['GPIO_JTAG1_CS'])
except:
    gpio_jtag0_cs = None
    gpio_jtag1_cs = None
    
sp_option_passthrough = ''

if len(sys.argv) < 2:
  print('No arguments\n Usage example : staplcmd i8 1 2 i10 deadface fe0dfe0f')
  print('will do:\nIRSCAN $8; DRSCAN 32 $1; DRSCAN 32 $2;')
  print('IRSCAN $10;  DRSCAN 32 $deadface; DRSCAN 32 $fe0dfe0f;')
  exit()

f = open('/run/shm/stapl.stp','w')
f.write('ACTION	TRANS = DO_TRANS;\n')
f.write('DATA PARAMETERS;\n')
f.write('BOOLEAN idcode_data[32*10];\n')
f.write('BOOLEAN irdata[10*32];\n')
f.write('ENDDATA;\n')

f.write('PROCEDURE DO_TRANS USES PARAMETERS;\n')
splayer_option = ''
work_with_carrier = 0

for s in sys.argv[1:]:
  if s == '-g': #use second JTAG chain
    splayer_option = '-g'
    continue
  if s == '-c': # set the path to work with carrier boards
    import wiringpi2
    wiringpi2.wiringPiSetupSys()
    work_with_carrier = gpio_jtag0_cs	# GPIO for the carrier select[0] line in RPiLVDS board
    sp_option_passthrough = os.environ['SP_OPTION_PASSTHROUGH']    
    continue
  #if s== '-o': #StaplPlayer will be called with -o option
  #  sp_option_passthrough = '-o'
  #  continue
  if s[0] == 'i':
    f.write('IRSCAN 8, $' + s[1:] + ', CAPTURE irdata[7..0];\n')
  else:
    f.write('DRSCAN 32, $' + s.rjust(8,'0') + ', CAPTURE idcode_data[31..0];\n')
    f.write('EXPORT "Shifted Out:", idcode_data[31..0];\n')
f.write('ENDPROC;\n')
f.close()

print("work_with_carrier="+str(work_with_carrier))
print("sp_option_passthrough="+sp_option_passthrough) 

if (work_with_carrier != 0):	# set route to carrier board
  if (splayer_option == '-g'):
     work_with_carrier = gpio_jtag1_cs	# GPIO for the carrier select[1] line in RPiLVDS board
  wiringpi2.pinMode(work_with_carrier,1)
  print('Executing wiringpi2.digitalWrite('+str(work_with_carrier)+',1)')
  wiringpi2.digitalWrite(work_with_carrier,1)
  if wiringpi2.digitalRead(work_with_carrier) != 1 :
    print('ERROR JTAG path through FEM using GPIO pin ' + str(work_with_carrier) + ' was not established')
    print('Did you forget "gpio export '+ str(work_with_carrier) + ' out" after reboot?') 
    exit(1) 

#print("Stapl instructions:\n")
#f = open('stapl.stp','r')
#for s in f:
#  print(s),
#f.close()

# execute action
import subprocess
cmdline = 'StaplPlayer ' + splayer_option + ' ' + sp_option_passthrough +' -aTRANS /run/shm/stapl.stp'
print('Executing:'+cmdline)

p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
  print line,
retval = p.wait()

if (work_with_carrier != 0):
  print('Executing wiringpi2.digitalWrite('+str(work_with_carrier)+',0)')
  wiringpi2.digitalWrite(work_with_carrier,0)
  if wiringpi2.digitalRead(work_with_carrier) != 0 :
    print('ERROR JTAG path through FEM using GPIO pin ' + str(work_with_carrier) + ' was not closed')


