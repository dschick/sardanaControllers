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

"""This file contains the code for an hypothetical Springfield motor controller
used in documentation"""

import visa, time

from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Description, DefaultValue


class kepcoController(MotorController):
    
    ctrl_properties = {'resource': {Type: str, Description: 'GPIB resource', DefaultValue: 'GPIB0::6::INSTR'}}
    
    MaxDevice = 1
    
    def __init__(self, inst, props, *args, **kwargs):
        super(kepcoController, self).__init__(
            inst, props, *args, **kwargs)

        self.rm = visa.ResourceManager('@py')
        self.inst = self.rm.open_resource(self.resource)
        print 'Kepco Initialization: ',
        idn = self.inst.query('*IDN?')
        if idn:
            print idn,
        else:
            print 'NOT initialized!'
        # initialize hardware communication        
        self._motors = {}
        self._isMoving = None
        self._moveStartTime = None
        self._threshold = 0.05
        self._target = None
        self._timeout = 10

    def AddDevice(self, axis):
        self._motors[axis] = True
        self.inst.write('FUNC:MODE CURR')
        self.inst.write('CURR:MODE FIX')
        self.inst.write('CURR:LIM:NEG 1.5')
        self.inst.write('CURR:LIM:POS 1.5')
        self.inst.write('OUTP ON')

    def DeleteDevice(self, axis):
        del self._motors[axis]

    def StateOne(self, axis):
        limit_switches = MotorController.NoLimitSwitch
        pos = self.ReadOne(axis)
        now = time.time()
        
        try:
            if self._isMoving == False:
                state = State.On
            elif self._isMoving & (abs(pos-self._target) > self._threshold): 
                # moving and not in threshold window
                if (now-self._moveStartTime) < self._timeout:
                    # before timeout
                    state = State.Moving
                else:
                    # after timeout
                    self._log.warning('Kepco Timeout')
                    self._isMoving = False
                    state = State.On
            elif self._isMoving & (abs(pos-self._target) <= self._threshold): 
                # moving and within threshold window
                self._isMoving = False
                state = State.On
                #print('Kepco Tagret: %f Kepco Current Pos: %f' % (self._target, pos))
            else:
                state = State.Fault
        except:
            state = State.Fault
        
        return state, 'some text', limit_switches

    def ReadOne(self, axis):
        res = float(self.inst.query('MEAS:CURR?'))
        time.sleep(0.001)      
        return res

    def StartOne(self, axis, position):
        self._moveStartTime = time.time()
        self._isMoving = True
        self._target = position
        cmd = 'CURR {:f}'.format(position)
        time.sleep(0.01)
        self.inst.write(cmd)

    def StopOne(self, axis):
        pass

    def AbortOne(self, axis):
        pass

    
