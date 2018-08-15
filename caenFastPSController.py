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

import socket, time

from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Description, DefaultValue


class caenFastPSController(MotorController):
    ctrl_properties = {'ip': {Type: str, Description: 'ip or hostname', DefaultValue: 'caen-fastps.hhg.lab'},
                       'port': {Type: int, Description: 'port', DefaultValue: 10001},
                       }
    
    MaxDevice = 1
    
    def __init__(self, inst, props, *args, **kwargs):
        super(caenFastPSController, self).__init__(
            inst, props, *args, **kwargs)

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 
                                 socket.IPPROTO_TCP)
        self.conn.connect((self.ip, self.port))
        self.conn.settimeout(5)
        self.conn.setblocking(True)
        print 'CAEN FAST-PS Initialization'
        [_, idn] = self.__sendAndReceive('VER')
        if idn:
            print 'Initialized model: %s' % idn
        else:
            print 'CAEN FAST-PS is NOT initialized!'
        # initialize hardware communication        
        self._motors = {}
        self._isMoving = None
        self._moveStartTime = None
        self._threshold = 0.0001
        self._target = None
        self._timeout = 10
        
    def AddDevice(self, axis):
        self._motors[axis] = True
        self.__sendAndReceive('UPMODE:NORMAL')
        self.__sendAndReceive('LOOP:I')
        self.__sendAndReceive('MON')

    def DeleteDevice(self, axis):
        del self._motors[axis]

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
                self._log.warning('CAEN FAST-PS Timeout')
                self._isMoving = False
                state = State.On
        elif self._isMoving & (abs(pos-self._target) <= self._threshold): 
            # moving and within threshold window
            self._isMoving = False
            state = State.On
            #print('Kepco Tagret: %f Kepco Current Pos: %f' % (self._target, pos))
        else:
            state = State.Fault
        
        return state, 'some text', limit_switches

    def ReadOne(self, axis):
        [_, pos] = self.__sendAndReceive('MRI')
        return float(pos)

    def StartOne(self, axis, position):
        self._moveStartTime = time.time()
        self._isMoving = True
        self._target = position
        cmd = 'MWI:%f' % position
        self.__sendAndReceive(cmd)

    def StopOne(self, axis):
        pass

    def AbortOne(self, axis):
        pass

    def __sendAndReceive(self, command):
        try:
            self.conn.send(command + '\r')
            ret = self.conn.recv(1024)
            while (ret.find('\r\n') == -1):
                ret += self.conn.recv(1024)
        except socket.timeout:
            return [-2, '']
        except socket.error:
            print 'Socket error'
            return [-2, '']
        
        for i in range(len(ret)):
            if (ret[i] == ':'):
                return [str(ret[0:i]), ret[i+1:-2]]
        else:
            return [ret[:-2], '']  
