#!/usr/bin/env python3
'''Slow control through JTAG connector'''

#__version__ = 'v02 2019-09-19'#created
__version__ = 'v03 2019-09-20'# gpiozero lib is too slow

import sys,time
from timeit import default_timer as timer
#from gpiozero import LEDBoard,Button
import RPi.GPIO as GPIO
TCK,TMS,TDI,TDO = 4,17,18,27

class UJTAG():
    def __init__(self,dbg=False):
        global Dbg
        Dbg = dbg
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TCK, GPIO.OUT)
        GPIO.setup(TMS, GPIO.OUT)
        GPIO.setup(TDI, GPIO.OUT)
        GPIO.setup(TDO, GPIO.IN)
        self.cmi = (TCK,TMS,TDI)
        self.lastTDI = None
        self.lastTMS = None
                
    def __del__(self):
        #self.spi.close()
        pass
        
    def _tdo(self):
        #return int(self.pinTDO.is_pressed)
        return(GPIO.input(TDO))
            
    def board_info(self):
        from gpiozero import pi_info
        print('{0}'.format(pi_info()))
        #print('{0:full}'.format(pi_info()))
        #print('{0:board}'.format(pi_info()))
        #print('{0:specs}'.format(pi_info()))
        #print('{0:headers}'.format(pi_info()))
    
    def _tms_tdi(self,tms,tdi):
        #print('tms%i,tdi%i'%(tms,tdi))
        #GPIO.output(TMS,tms)
        #GPIO.output(TDI,tdi)
        GPIO.output(self.cmi,(0,tms,tdi))
        GPIO.output(TCK,1)
        #GPIO.output(self.cmi,(1,tms,tdi))
        GPIO.output(TCK,0)
        return GPIO.input(TDO)
        
    def reset(self,go2run=False):
        '''go to Idle or Run state through Test-Logic-Reset from any state'''
        for i in range(5):
            self._tms_tdi(1,0)
        self._tms_tdi(0,0)
        if go2run:
            self._tms_tdi(1,0)
        
    def irscan(self,data,width=8):
        '''do irscan starting from Run finish in Run state'''
        #self._tms_tdi(0,0)
        #self._tms_tdi(1,0)
        self._tms_tdi(1,0)
        self._tms_tdi(0,0)#>capture
        self._tms_tdi(0,0)#>shift-ir
        #print('>irshift')
        for i in range(width-1): #shift
            #self._tms_tdi(0,(data>>(width-i-1))&1)
            self._tms_tdi(0,data&1)
            data = data >> 1
        self._tms_tdi(1,data&1)#>exit-ir
        self._tms_tdi(1,0)#>update-ir
        self._tms_tdi(1,0)#>Run
    
    def drscan(self,data,width=32,go2idle=False):
        '''do drscan starting from Run finish in Run state'''
        self._tms_tdi(0,0)#>capture
        self._tms_tdi(0,0)#>shift-dr
        d = 0
        #print('>drshift')
        for i in range(width-1): #shift
            #tdo = self._tms_tdi(0,(data>>(width-i-1))&1)
            tdo = self._tms_tdi(0,data&1)
            data = data >> 1
            d |= tdo << i+1
        tdo = self._tms_tdi(1,data&1)#>exit-dr
        d |= tdo
        self._tms_tdi(1,0)#>update-dr
        self._tms_tdi(0 if go2idle else 1, 0)#>Idle or Run
        return d
        
#````````````````````````````Test program`````````````````````````````````````
if __name__ == "__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__)#\
      #,formatter_class=RawTextHelpFormatter)
    parser.add_argument('-d','--dbg', action='store_true', help='debugging')
    parser.add_argument('-i','--info',action='store_true',help='Board info')
    parser.add_argument('-p','--power',default=None,
      help='Power up (-p1) or down (-p0) all devices')
    parser.add_argument('-n','--n',type=int,default=1,help='number of cycles')
    pargs = parser.parse_args()
    
    uj = UJTAG()
    if pargs.info:
        uj.board_info()
        sys.exit()
        
    uj.reset(go2run = True)
    print(pargs.power)
    if pargs.power != None:
        uj.irscan(0x16)
        d = 0xf000 if pargs.power == '0' else 0
        q = uj.drscan(d)
        print('captured:'+hex(q)+', written:'+hex(d))
        sys.exit()

    ts = timer()
    for i in range(pargs.n):
        uj.irscan(0x1d)
        d = 0xc00c7007
        q = uj.drscan(d)
        print('captured:'+hex(q)+', written:'+hex(d))
        q = uj.drscan(d)
        print('captured:'+hex(q)+', written:'+hex(d))
        
        #the shadow register 9d should show the same but it shows 0
        #uj.irscan(0x9d)
        #q = uj.drscan(0)
        #print('captured from 9d:'+hex(q))        

        #board reset
        #uj.irscan(0x10)
        #uj.drscan(0x1000)
        #uj.drscan(0x0000)

        #print('cycle %i, '%i + str(timer()-ts))
        #time.sleep(1)
    print('cycles %i, '%pargs.n + str(timer()-ts))
        
