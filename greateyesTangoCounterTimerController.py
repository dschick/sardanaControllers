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
from tango import DeviceProxy
from sardana.pool.controller import TwoDController, Referable, Type, Description, DefaultValue, FGet, FSet

class greateyesTangoCounterTimerController(TwoDController, Referable):
    """The most basic controller intended from demonstration purposes only.
    This is the absolute minimum you have to implement to set a proper counter
    controller able to get a counter value, get a counter state and do an
    acquisition.

    This example is so basic that it is not even directly described in the
    documentation"""
    ctrl_properties = {'tangoFQDN': {Type: str, 
                              Description: 'The FQDN of the greateyes tango DS', 
                              DefaultValue: 'greateyes.hhg.lab'},
                       }

    axis_attributes = {
             "SavingEnabled": {
                Type: bool,
                FGet: "isSavingEnabled",
                FSet: "setSavingEnabled",
                Description: ("Enable/disable saving of images in HDF5 files."
                              " Use with care in high demanding (fast)"
                              " acquisitions. Trying to save at high rate may"
                              " hang the acquisition process."),
             }
        }

    def AddDevice(self, axis):
        self._axes[axis] = {}

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        TwoDController.__init__(self,inst,props, *args, **kwargs)
        print 'GreatEyes Tango Initialization ...',
        self.proxy = DeviceProxy(self.tangoFQDN)
        print 'SUCCESS'
        self._axes = {}
        
    def ReadOne(self, axis):
        """Get the specified counter value"""    
        #print(self._SavingEnabled)
        #print('Image saved to: {:s}'.format(self.proxy.LastSavedImage))
        return self.proxy.image
    
    def RefOne(self, axis):
        return self.proxy.LastSavedImage
    
    def SetAxisPar(self, axis, parameter, value):
#        if parameter == "value_ref_pattern":
#            print('value_ref_pattern ' + str(value))
#        elif parameter == "value_ref_enabled":
#            print('value_ref_enabled ' + str(value))
#            self.setSavingEnabled(axis, value)
        pass

    def StateOne(self, axis):
        """Get the specified counter state"""
#            
        return self.proxy.State(), "Counter is acquiring or not"

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        # set exporsure time of GE cam
        self.proxy.ExposureTime = float(value)
    
    def LoadOne(self, axis, value, repetitions, latency):
        pass

    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        self.proxy.StartAcq()
        return

    def StopOne(self, axis):
        """Stop the specified counter"""
        self.proxy.StopAcq()
    
    def AbortOne(self, axis):
        """Abort the specified counter"""
        self.proxy.StopAcq()

    def isSavingEnabled(self, axis):
        return bool(self.proxy.SaveImageFiles)

    def setSavingEnabled(self, axis, value):
        self.proxy.SaveImageFiles = bool(value)