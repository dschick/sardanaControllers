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

from pyagilis.controller import AGAP
from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Description, DefaultValue


class AgilisCONEXagapController(MotorController):
    ctrl_properties = {'port': {Type: str, Description: 'The port of the rs232 device', DefaultValue: '/dev/ttyAGILIS2'}}
    
    MaxDevice = 2
    
    def __init__(self, inst, props, *args, **kwargs):
        super(AgilisCONEXagapController, self).__init__(
            inst, props, *args, **kwargs)

        # initialize hardware communication
        self.agilis = AGAP(self.port)
        # first query will somehow timeout
        self.agilis.getStatus()
        print('AGAP Controller Initialization ...'),
        if self.agilis.getStatus() == 0: # configuration mode
            self._log.info('Controller is in configuration mode!')
            print('FAILED due to configuration mode!')
        print('SUCCESS on port %s' % self.port)
        # do some initialization
        self._motors = {}

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
        state = self.agilis.getStatus()
                
        return self.StateMap[state], 'some text', limit_switches

    def ReadOne(self, axis):
        positions = self.agilis.getCurrentPosition()
        return float(positions[axis])
        
    def PreStartAll(self):
        # clear the local motion information dictionary
        self._moveable_info = []

    def StartOne(self, axis, position):
        # store information about this axis motion
        motion_info = axis, position
        self._moveable_info.append(motion_info)

    def StartAll(self):
        self.agilis.moveAbsolute(self._moveable_info)

    def StopOne(self, axis):
        self.agilis.stop()

    def AbortOne(self, axis):
        self.agilis.stop()

    
