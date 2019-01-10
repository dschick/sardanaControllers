from sardana.pool.controller import PseudoCounterController

import PyTango, taurus

class pseudoCounterAltOnTest(PseudoCounterController):
    """ A simple pseudo counter which receives two counter values (I and I0)
        and returns I/I0"""

    counter_roles        = ('I1',)
    pseudo_counter_roles = ('O1', 'O2', 'O3',)
    value = [0,0,0]
    field = 0
    proxies = [PyTango.AttributeProxy('expchan/keithleyctrl/0/Value'),
               PyTango.AttributeProxy('expchan/epochctrl/0/Value'),
               PyTango.AttributeProxy('expchan/epicszctrl/0/Value'),]
#    proxies = [taurus.Attribute('tango://tesla:10000/pc/altonctrl/1/Value'),
#               taurus.Attribute('tango://tesla:10000/pc/altonctrl/2/Value'),
#               taurus.Attribute('tango://tesla:10000/pc/altonctrl/3/Value'),]
    

    
    def __init__(self, inst, props):  
        PseudoCounterController.__init__(self, inst, props)
        self.magnetTau = taurus.Attribute('tango://tesla:10000/motor/kepcoctrl/0/position')
        self.magnetTau.changePollingPeriod(0.5)
        #self.magnetTau.poll()
        #self.magnet = PyTango.DeviceProxy("motor/kepcoctrl/0")
        
    
    def Calc(self, axis, counters):
        #if axis == 1:            
        self.field = self.magnetTau.read().value
        #self.field = self.magnet.getPosition()
        print(axis)
        print(self.field)
        print("-----")
        
        if self.field < 0:
            self.value[axis-1] = self.proxies[axis-1].read().value
    
        return self.value[axis-1]