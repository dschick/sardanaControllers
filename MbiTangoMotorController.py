from PyTango import DeviceProxy

from sardana import State, DataAccess
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Access, Description, DefaultValue


class MbiTangoMotorController(MotorController):
    
    MaxDevice = 99
    
    axis_attributes = {
        'Tango_Device': {
            Type: str,
            Description: 'The Tango Device'\
                ' (e.g. domain/family/member)',
            Access: DataAccess.ReadWrite
        },
    }
    
    def __init__(self, inst, props, *args, **kwargs):
        super(MbiTangoMotorController, self).__init__(
            inst, props, *args, **kwargs)
        
        self._log.info('Initialized')
        # do some initialization
        self.axisAttributes = {}

    def AddDevice(self, axis):
        self._log.info('adding axis {:d}'.format(axis))
        self.axisAttributes[axis] = {}
        self.axisAttributes[axis]['Proxy'] = None

    def DeleteDevice(self, axis):
        self._log.info('delete axis {:d}'.format(axis))
        del self.axisAttributes[axis]

    def StateOne(self, axis):
        state = self.axisAttributes[axis]['Proxy'].command_inout("State")
        status = self.axisAttributes[axis]['Proxy'].command_inout("Status")
        switch_state = MotorController.NoLimitSwitch
        limit_plus = self.axisAttributes[axis]['Proxy'].read_attribute("limit_plus").value
        limit_minus = self.axisAttributes[axis]['Proxy'].read_attribute("limit_minus").value
        if limit_plus:
            switch_state |= MotorController.UpperLimitSwitch
            state = State.Alarm
        elif limit_minus:
            switch_state |= MotorController.LowerLimitSwitch
            
        if (state != State.Moving) & (limit_plus | limit_minus):
            state = State.Alarm
        return state, status, switch_state

    def ReadOne(self, axis):
        ret = self.axisAttributes[axis]['Proxy'].read_attribute("Position").value
        return ret
        
    def StartOne(self, axis, position):
        self.axisAttributes[axis]['Proxy'].write_attribute("Position", position)

    def StopOne(self, axis):
        self.axisAttributes[axis]['Proxy'].command_inout("Stop")

    def AbortOne(self, axis):
        self.axisAttributes[axis]['Proxy'].command_inout("Stop")

    def SetPar(self, axis, name, value):
        if self.axisAttributes[axis]['Proxy']:
            if name == 'velocity':
                self.axisAttributes[axis]['Proxy'].write_attribute("velocity", value)
            elif name in ['acceleration', 'deceleration']:
                self.axisAttributes[axis]['Proxy'].write_attribute("acceleration", value)
            elif name == 'step_per_unit':
                self.axisAttributes[axis]['Proxy'].write_attribute("step_per_unit", value)
            else:
                self._log.debug('Parameter %s is not set' % name)

    def GetPar(self, axis, name):
        if self.axisAttributes[axis]['Proxy']:
            if name == 'velocity':
                result = self.axisAttributes[axis]['Proxy'].read_attribute("velocity").value
            elif name in ['acceleration', 'deceleration']:
                result = self.axisAttributes[axis]['Proxy'].read_attribute("acceleration").value
            elif name == 'step_per_unit':
                result = self.axisAttributes[axis]['Proxy'].read_attribute("step_per_unit").value
            else:
                result = None
        else:
            result = None
        return result

    def GetAxisExtraPar(self, axis, name):
        return self.axisAttributes[axis][name]
    
    def SetAxisExtraPar(self, axis, name, value):
        if name == 'Tango_Device':
            self.axisAttributes[axis][name] = value
            try:
                self.axisAttributes[axis]['Proxy'] = DeviceProxy(value)
                self._log.info('axis {:d} DeviceProxy set to: {:s}'.format(axis, value))
            except Exception as e:
                self.axisAttributes[axis]['Proxy'] = None
                raise e

    def DefinePosition(self, axis, position):
        self.axisAttributes[axis]['Proxy'].command_inout("set_position", position)

    def SendToCtrl(self, cmd):
        """
        Send custom native commands. The cmd is a space separated string
        containing the command information. Parsing this string one gets
        the command name and the following are the arguments for the given
        command i.e.command_name, [arg1, arg2...]

        :param cmd: string
        :return: string (MANDATORY to avoid OMNI ORB exception)
        """
        # Get the process to send
        mode = cmd.split(' ')[0].lower()
        args = cmd.strip().split(' ')[1:]

        if mode == 'homing':
            try:
                if len(args) == 2:
                    axis, direction = args
                    axis = int(axis)
                    direction = int(direction)
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)

            self._log.info('Starting homing for axis {:d} in direction id {:d}'.format(axis, direction))
            try:
                if direction == 0:
                    self.axisAttributes[axis]['Proxy'].command_inout("Homing_Minus")
                else:
                    self.axisAttributes[axis]['Proxy'].command_inout("Homing_Plus")
            except Exception as e:
                self._log.error(e)
