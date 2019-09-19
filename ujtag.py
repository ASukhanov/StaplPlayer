#!/usr/bin/env python3

__version__ = 'v02 2019-09-19'#created
from gpiozero import LEDBoard,Button

class UJTAG():
    def __init__(self,dbg=False):
        global Dbg
        Dbg = dbg
        #DRS4GLO pins
        #self.pinTDO = Button('BOARD13')
        self.pinTDO = Button(27)
        #self.pinCMI = LEDBoard('BOARD07','BOARD11','BOARD12')
        self.pinCMI = LEDBoard(4,17,18)
                
    def __del__(self):
        self.spi.close()
        
    def tck_tms_tdi(self,cmi):
        self.cmi.value = cmi
        
    def tdo(self):
        return self.pinTDO.is_pressed
            
    def board_info(self):
        from gpiozero import pi_info
        print('{0}'.format(pi_info()))
        #print('{0:full}'.format(pi_info()))
        #print('{0:board}'.format(pi_info()))
        #print('{0:specs}'.format(pi_info()))
        #print('{0:headers}'.format(pi_info()))
    