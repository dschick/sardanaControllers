from sardana.pool.controller import PseudoCounterController
from PyTango import DeviceProxy

class pseudoCounterAltOn(PseudoCounterController):
    """ A  pseudo counter which remebers the input for negative magnetic
    fields and returns it at positive fields"""

    counter_roles        = ('I',)
    pseudo_counter_roles = ('O',)
    value = 0
    field = 0
    
    def __init__(self, inst, props):  
        PseudoCounterController.__init__(self, inst, props)
        self.magnetState = DeviceProxy("hhg/MagnetState/moke")
    
    def Calc(self, axis, counters):
        counter = counters[0]
        self.field = self.magnetState.magnet
        
        if self.field < 0:
            self.value = counter        
    
        return self.value