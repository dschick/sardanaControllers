##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import visa, time

from sardana import State
from sardana.pool.controller import ZeroDController
from sardana.pool.controller import Type, Description, DefaultValue

class keithley6430ZeroDController(ZeroDController):
    """This class represents a dummy Sardana 0D controller."""
    
    ctrl_properties = {'resource': {Type: str, Description: 'GPIB resource', DefaultValue: 'GPIB0::3::INSTR'}}
    
    MaxDevice = 1    

    def __init__(self, inst, props, *args, **kwargs):
        ZeroDController.__init__(self, inst, props, *args, **kwargs)

        self.rm = visa.ResourceManager('@py')
        self.inst = self.rm.open_resource(self.resource)
        print 'Keithley 6430 Initialization: ',
        idn = self.inst.query('*IDN?')
        if idn:
            print idn,
        else:
            print 'NOT initialized!'

        # settings
        self.inst.write('*RST')
        self.inst.write('REN')
        self.inst.write(':INIT')
        self.inst.write(':SENS:FUNC "CURR"')
        self.inst.write(':CURR:RANGE:AUTO ON')
        self.inst.write(':OUTP ON')

    def AddDevice(self, ind):
        pass

    def DeleteDevice(self, ind):
        pass

    def StateOne(self, ind):
        return State.On, "OK"

    def ReadOne(self, ind):
        res = self.inst.query(':READ?')        
        return float(res.encode('utf8').split(',')[1])