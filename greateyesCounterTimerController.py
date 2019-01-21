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

from sardana import State
from sardana.pool.controller import CounterTimerController, Type, Description, DefaultValue
import socket
import struct
import json
import numpy as np

class greatEyes:
    def __init__(self, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.connect((ip, port))
        
    def writeRead(self, cmd):
        self.write(cmd)        
        return(self.read())
    
    def acquireImage(self, intTime):
        self.write('SETTIME' + intTime)
        self.writeRead('ACQUIRE')
    
    def write(self, cmd):
        # write
        cmd_bytes = len(cmd)
        cmd_bytes_string = struct.pack('>I', cmd_bytes)

        self.s.send(cmd_bytes_string)
        self.s.sendall(cmd)
            
    def read(self):        
        # read
        ack_bytes_string = self.s.recv(4)
        #print(ack_bytes_string)
        ack_bytes = struct.unpack('>I', ack_bytes_string[:4])[0]
        #print(ack_bytes)
        
        # Look for the response
#        amount_received = 0
#        ack = b''
#        
#        while amount_received < ack_bytes:
#            data = self.s.recv(4096)
#            amount_received += len(data)
#            ack += data
        
        ack = self.s.recv(ack_bytes)
        
        return(ack)
    
    def __del__(self):
        self.s.close() 

class greateyesCounterTimerController(CounterTimerController):
    """The most basic controller intended from demonstration purposes only.
    This is the absolute minimum you have to implement to set a proper counter
    controller able to get a counter value, get a counter state and do an
    acquisition.

    This example is so basic that it is not even directly described in the
    documentation"""
    ctrl_properties = {'IP': {Type: str, 
                              Description: 'The IP/FQDN of the greateyes labview server', 
                              DefaultValue: 'greateyes.hhg.lab'},
                        'port': {Type: int, 
                             Description: 'The port of the greateyes labview server', 
                             DefaultValue: 5000},
                       }
                        
    def AddDevice(self, axis):
        self._axes[axis] = {}

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        super(greateyesCounterTimerController,
              self).__init__(inst, props, *args, **kwargs)
        print 'GreatEyes Initialization ...',
        self.ge = greatEyes(self.IP, self.port)
        print 'SUCCESS'
        self.data = []
        self.isAquiring = False
        self._axes = {}
        
    def ReadOne(self, axis):
        """Get the specified counter value"""
        
        if axis == 0:
            peaks = json.loads(self.ge.writeRead(b'GET_PEAKS'))
            self.data = np.array(peaks, dtype=float).flatten()
            rel = self.data[0:10]/self.data[10:20]
            self.data = np.append(self.data, rel)
         
        return self.data[axis]

    def StateOne(self, axis):
        """Get the specified counter state"""
        
        if axis == 0:
            res = self.ge.writeRead(b'GET_STATUS')
            status = int(res.decode("utf-8").split(' ')[1])
            if (status == -1) or (status == 1):
                self.isAquiring = False
            else:
                self.isAquiring = True
            
        if self.isAquiring:
           return State.Moving, "Counter is acquiring"
        else:                
            return State.On, "Counter is stopped"
        
    def StartOne(self, axis, value=None):
        """acquire the specified counter"""        
        return
            
    
    def StartAll(self):
        self.isAquiring = True
        self.ge.writeRead(b'ACQUIRE')
        #time.sleep(0.1)
    
    def LoadOne(self, axis, value, repetitions):
        pass

    def StopOne(self, axis):
        """Stop the specified counter"""
        pass
    
    def AbortOne(self, axis):
        """Abort the specified counter"""
        pass
    
    def SendToCtrl(self, cmd):
        """
        Send custom native commands. The cmd is a space separated string
        containing the command information. Parsing this string one gets
        the command name and the following are the arguments for the given
        command i.e.command_name, [arg1, arg2...]

        :param cmd: string
        :return: string (MANDATORY to avoid OMNI ORB exception)
        """
        mode = cmd.split(' ')[0].lower()
        args = cmd.strip().split(' ')[1:]
        
        print(mode)
        print(args)

        if mode == "setpath":
            self.ge.writeRead(b'SET_FILENAME {:}'.format(args[0]))