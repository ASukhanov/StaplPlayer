#!/usr/bin/env python3
'''Slow Control through JTAG connector'''

__version__ = 'v07 2019-09-25'#docstrings

import sys,time
from timeit import default_timer as timer
try:
    import RPi.GPIO as GPIO
except Exception as e:
    print('WARNING:'+str(e))
TCK,TMS,TDI,TDO = 4,17,18,27

class UJTAG():
    '''Interface to FPGA fabric using JTAG connector'''
    def __init__(self,dbg=False):
        '''Configure GPIO channels'''
        global Dbg
        Dbg = dbg
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TCK, GPIO.OUT)
            GPIO.setup(TMS, GPIO.OUT)
            GPIO.setup(TDI, GPIO.OUT)
            GPIO.setup(TDO, GPIO.IN)
        except Exception as e:
            print('WARNING:'+str(e))
        self.cmi = (TCK,TMS,TDI)
        self.lastTDI = None
        self.lastTMS = None
        self.lastIR = None
                
    def __del__(self):
        '''Cleanup, return all used channels to inputs with no pull up/down'''
        #GPIO.cleanup()
        pass
        
    def _tdo(self):
        # Return state of the TDO line
        return(GPIO.input(TDO))
            
    def board_info(self):
        print('UJTAG host:'+str(GPIO.RPI_INFO))
    
    def _tms_tdi(self,tms,tdi):
        #print('tms%i,tdi%i'%(tms,tdi))
        GPIO.output(self.cmi,(0,tms,tdi))
        GPIO.output(TCK,1)
        GPIO.output(TCK,0)
        return GPIO.input(TDO)
        
    def reset(self,go2run=False):
        '''Go to Idle or Run state through Test-Logic-Reset from any state'''
        for i in range(5):
            self._tms_tdi(1,0)
        self._tms_tdi(0,0)
        if go2run:
            self._tms_tdi(1,0)
        
    def irscan(self,ir,width=8):
        '''Do irscan starting from Run state finish in Run state'''
        if ir == self.lastIR:
            return
        self.lastIR = ir
        self._tms_tdi(1,0)
        self._tms_tdi(0,0)#>capture
        self._tms_tdi(0,0)#>shift-ir
        #print('>irshift')
        for i in range(width-1): #shift
            self._tms_tdi(0,ir&1)
            ir = ir >> 1
        self._tms_tdi(1,ir&1)#>exit-ir
        self._tms_tdi(1,0)#>update-ir
        self._tms_tdi(1,0)#>Run
    
    def drscan(self,data,ir=None,width=32,go2idle=False):
        '''Do drscan starting from Run state finish in Run state'''
        if ir is not None:
            self.irscan(ir)
        self._tms_tdi(0,0)#>capture
        self._tms_tdi(0,0)#>shift-dr
        d = 0
        #print('>drshift')
        for i in range(width-1): #shift
            tdo = self._tms_tdi(0,data&1)
            data = data >> 1
            d |= tdo << i+1
        tdo = self._tms_tdi(1,data&1)#>exit-dr
        d |= tdo
        self._tms_tdi(1,0)#>update-dr
        self._tms_tdi(0 if go2idle else 1, 0)#>Idle or Run
        return d
uj = UJTAG()

class CSR():
    '''UJTAG-compatible Command and Status Register''' 
    def __init__(self,ir, d={}, q={}, name='?'):
        '''Create the CSR
        d: specifies the input bit fields
        q: specifies the output bit fields
        '''
        self.ir = ir
        self.name = name
        self.lastQ = 0
        self.dFields = {}# map of input fields
        self.qFields = {}# map of output fields
        
        def _set_fields(items,fields):
            for key,bitRange in items:
                startBit,endBit = bitRange
                mask = 0
                for i in range(startBit,endBit+1):
                    mask |= 1<<i
                fields[key] = startBit,mask
        _set_fields(q.items(),self.qFields)
        _set_fields(d.items(),self.dFields)        
            
    def update(self,q=0):
        '''Read current value, set new value to q, current value is returned'''
        d = uj.drscan(q,self.ir)
        self.lastQ = q
        return d

    def fields(self,dq='d'):
        '''Return list of BitFields'''
        return self.qFields.keys() if dq=='q' else self.dFields.keys()
        
    def get_field(self,name):
        '''Return value of the named field'''
        #print('CSR getter '+str(name))
        d = self.update()
        #print('BitField Getter called: %s='%self.name+hex(d))
        startBit,mask = self.dFields[name]
        d = (d & mask) >> startBit
        return d
        
    def set_field(self,name,value):
        '''Set new value to the named field'''
        startBit,mask = self.qFields[name]
        qClearField = self.lastQ & ~mask
        q = qClearField | ((value << startBit)&mask)
        d = self.update(q)
        print('Setter called: %s=%s from %s, '%(name,hex(q),hex(d)))
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
        uj.irscan(0x10)
        ir10d = uj.drscan(0)
        print('IR10:'+hex(ir10d))

        uj.irscan(0x90)
        ir90d = uj.drscan(0)
        print('IR10_Shadow:'+hex(ir90d))
        if ir10d != ir90d:
            print('WARNING: Shadow register IR90='+hex(ir90d)\
            +'expected:'+hex(ir10d))
        
        uj.irscan(0x1d)
        d = 0xc00c7007
        q = uj.drscan(d)
        print('captured:'+hex(q)+', written:'+hex(d))
        q = uj.drscan(d)
        print('captured:'+hex(q)+', written:'+hex(d))
    print('cycles %i, '%pargs.n + str(timer()-ts))
        
