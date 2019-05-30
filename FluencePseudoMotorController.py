import numpy as np

from sardana.pool.controller import PseudoMotorController
from sardana.pool.controller import Type, Description, DefaultValue, Access, FGet, FSet, DataAccess, Memorize, Memorized


class fluencePseudoMotorController(PseudoMotorController):
    """A Slit pseudo motor controller for handling gap and offset pseudo 
       motors. The system uses to real motors sl2t (top slit) and sl2b (bottom
       slit)."""
        
    axis_attributes  = {'pumpHor': {Type: float, Description: 'beam diameter horizontal FWHM in um', DefaultValue: 0.01, Memorized: Memorize},
                        'pumpVer': {Type: float, Description: 'beam diameter vertical FWHM in um', DefaultValue: 0.01, Memorized: Memorize},
                        'refl': {Type: float, Description: 'sample reflectivity', DefaultValue: 0, Memorized: Memorize},
                        'repRate': {Type: float, Description: 'laser repetition rate', DefaultValue: 3000, Memorized: Memorize},
                       }
    
    
    pseudo_motor_roles = ("OutputMotor",)
    motor_roles = ("InputMotor",)
        
    def __init__(self, inst, props):  
        PseudoMotorController.__init__(self, inst, props)
    
    def CalcPhysical(self, axis, pseudo_pos, curr_physical_pos):
        fluence = pseudo_pos[axis-1]
        trans   = 1-(self.refl/100)
        power = float((fluence*self.repRate/1000*np.pi*self.pumpHor/10000/2*self.pumpVer/10000/2)/trans)
        return power
    
    def CalcPseudo(self, axis, physical_pos, curr_pseudo_pos):
        power = physical_pos[axis-1]        
        trans   = 1-(self.refl/100)
        fluence = float(power*trans/(self.repRate/1000*np.pi*self.pumpHor/10000/2*self.pumpVer/10000/2))
        return fluence
    
    def GetAxisExtraPar(self, axis, name):
        """ Get Smaract axis particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        name = name.lower()
        
        if name == 'pumphor':
            result = self.pumpHor
        elif name == 'pumpver':
            result = self.pumpVer
        elif name == 'refl':
            result = self.refl
        elif name == 'reprate':
            result = self.repRate
        else:
            raise ValueError('There is not %s attribute' % name)
        return result

    def SetAxisExtraPar(self, axis, name, value):
        """ Set Smaract axis particular parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """
        name = name.lower()
        if name == 'pumphor':
            self.pumpHor = value
        elif name == 'pumpver':
            self.pumpVer = value
        elif name == 'refl':
            self.refl = value
        elif name == 'reprate':
            self.repRate = value
        else:
            raise ValueError('There is not %s attribute' % name)
        