from subprocess import call
from time import sleep

for ii in range(100):
#    call(['gpio','readall'])
#    call('sudo ./stapl_player -v -aREAD_IDCODE idcode.stp', shell=True)
    call("sudo ./stapl_player -r -aREAD_IDCODE idcode.stp",shell=True)
    sleep(1)	
