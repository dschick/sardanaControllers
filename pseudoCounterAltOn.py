from sardana.pool.controller import PseudoCounterController
import PyTango

class pseudoCounterAltOn(PseudoCounterController):
    """ A simple pseudo counter which receives two counter values (I and I0)
        and returns I/I0"""

    counter_roles        = ('I1', 'I2', 'I3', 'I4', 'I5', 'I6',  'I7', 'I8', 'I9', 'I10', \
                            'I11', 'I12', 'I13', 'I14', 'I15', 'I16', 'I17', 'I18', 'I19', 'I20', \
                            'I21', 'I22', 'I23', 'I24', 'I25', 'I26', 'I27',  'I28', 'I29', 'I30', \
                            'I31', 'I32', )
    pseudo_counter_roles = ('O1', 'O2', 'O3', 'O4', 'O5', 'O6',  'O7',  'O8',  'O9',  'O10', \
                            'O11', 'O12', 'O13', 'O14', 'O15', 'O16',  'O17',  'O18',  'O19',  'O20', \
                            'O21', 'O22', 'O23', 'O24', 'O25', 'O26',  'O27',  'O28',  'O29',  'O30', \
                            'O31', 'O32', )
    value = [0,0,0,0,0,0,0,0,0,0, \
             0,0,0,0,0,0,0,0,0,0, \
             0,0,0,0,0,0,0,0,0,0, \
             0,0,]
    field = 0
    
    def __init__(self, inst, props):  
        PseudoCounterController.__init__(self, inst, props)
        self.magnet = PyTango.DeviceProxy("motor/kepcoctrl/0")
    
    def Calc(self, axis, counters):
        counter = counters[axis-1]
        if axis == 1:
            self.field = self.magnet.position
        
        if self.field < 0:
            self.value[axis-1] = counter        
    
        return self.value[axis-1]