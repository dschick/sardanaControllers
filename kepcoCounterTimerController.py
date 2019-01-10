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

import time
from sardana import State
from sardana.pool.controller import CounterTimerController
import PyTango

class kepcoCounterTimerController(CounterTimerController):
    """The most basic controller intended from demonstration purposes only.
    This is the absolute minimum you have to implement to set a proper counter
    controller able to get a counter value, get a counter state and do an
    acquisition.

    This example is so basic that it is not even directly described in the
    documentation"""
    def AddDevice(self, axis):
        pass

    def DeleteDevice(self, axis):
        pass

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        super(kepcoCounterTimerController,
              self).__init__(inst, props, *args, **kwargs)
        self.int_time = 0
        self.start_time = 0
        self.magnet = PyTango.DeviceProxy("motor/kepcoctrl/0")

    def ReadOne(self, axis):
        """Get the specified counter value"""
        return self.magnet.position

    def StateOne(self, axis):
        """Get the specified counter state"""        
        if (time.time() - self.start_time) < self.int_time:
            return State.Moving, "Counter is acquiring"
        else:
            return State.On, "Counter is stopped"
        
    def StartOne(self, axis, value):
        """acquire the specified counter"""
        self.int_time = value
        self.start_time = time.time()

    def StartAll(self):
        pass

    def LoadOne(self, axis, value, repetitions):
        pass

    def StopOne(self, axis):
        """Stop the specified counter"""
        pass