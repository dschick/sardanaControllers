from sardana.pool.controller import PseudoCounterController
from sardana.taurus.core.tango.sardana.pool import registerExtensions
registerExtensions()
import taurus

class pseudoCounterAltOnTest(PseudoCounterController):
    """ A  pseudo counter which remebers the input for negative magnetic
    fields and returns it at positive fields"""

    counter_roles        = ('I',)
    pseudo_counter_roles = ('O',)
    value = 0
    field = 0
    
    def __init__(self, inst, props):  
        PseudoCounterController.__init__(self, inst, props)
        self.magnet = taurus.Device("kepco")
    
    def Calc(self, axis, counters):
        counter = counters[0]
        self.field = self.magnet.getPosition()
        
        if self.field < 0:
            self.value = counter        
    
        return self.value