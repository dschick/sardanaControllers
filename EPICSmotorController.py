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

import time, epics
from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Description, DefaultValue


class EPICSmotorController(MotorController):
    ctrl_properties = {'setpoint': {Type: str,
                                Description: 'The PV for the setpoint',
                                DefaultValue: 'HHG:MOTOR:SETPOINT'},
                       'readback': {Type: str,
                                Description: 'The PV for the readback',
                                DefaultValue: 'HHG:MOTOR:READBACK'}}
    
    MaxDevice = 1
    
    def __init__(self, inst, props, *args, **kwargs):
        super(EPICSmotorController, self).__init__(
            inst, props, *args, **kwargs)

        
        
        print('EPICS Motor Controller Initialization ...'),
        print('SUCCESS')
        # do some initialization
        self._motors = {}
        self._isMoving = None
        self._moveStartTime = None
        self._threshold = 0.05
        self._target = None
        self._timeout = 10

    def AddDevice(self, axis):
        self._motors[axis] = True

    def DeleteDevice(self, axis):
        del self._motors[axis]

    StateMap = {
        1: State.On,
        2: State.Moving,
        3: State.Fault,
    }

    def StateOne(self, axis):
        limit_switches = MotorController.NoLimitSwitch     
        pos = self.ReadOne(axis)
        now = time.time()
        
        if self._isMoving == False:
            state = State.On
        elif self._isMoving & (abs(pos-self._target) > self._threshold): 
            # moving and not in threshold window
            if (now-self._moveStartTime) < self._timeout:
                # before timeout
                state = State.Moving
            else:
                # after timeout
                self._log.warning('EPICS Motor Timeout')
                self._isMoving = False
                state = State.On
        elif self._isMoving & (abs(pos-self._target) <= self._threshold): 
            # moving and within threshold window
            self._isMoving = False
            state = State.On
            #print('Kepco Tagret: %f Kepco Current Pos: %f' % (self._target, pos))
        else:
            state = State.Fault
        
        return state, 'EPICS Motor', limit_switches  

    def ReadOne(self, axis):
        return float(epics.caget(self.readback))
        
    def StartOne(self, axis, position):
        self._moveStartTime = time.time()
        self._isMoving = True
        self._target = position
        epics.caput(self.setpoint, position)

    def StopOne(self, axis):
        pass

    def AbortOne(self, axis):
        pass

    