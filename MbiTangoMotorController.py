from PyTango import DeviceProxy

from sardana import State, DataAccess
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Access, Description


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
        self.axis_extra_pars = {}

    def AddDevice(self, axis):
        self._log.info('adding axis {:d}'.format(axis))
        self.axis_extra_pars[axis] = {}
        self.axis_extra_pars[axis]['Proxy'] = None

    def DeleteDevice(self, axis):
        self._log.info('delete axis {:d}'.format(axis))
        del self.axis_extra_pars[axis]

    def StateOne(self, axis):
        state = self.axis_extra_pars[axis]['Proxy'].command_inout("State")
        status = self.axis_extra_pars[axis]['Proxy'].command_inout("Status")
        switch_state = MotorController.NoLimitSwitch
        limit_plus = self.axis_extra_pars[axis]['Proxy'].read_attribute("hw_limit_plus").value
        limit_minus = self.axis_extra_pars[axis]['Proxy'].read_attribute("hw_limit_minus").value
        if limit_plus:
            switch_state |= MotorController.UpperLimitSwitch
            state = State.Alarm
        elif limit_minus:
            switch_state |= MotorController.LowerLimitSwitch
            
        if (state != State.Moving) & (limit_plus | limit_minus):
            state = State.Alarm
        return state, status, switch_state

    def ReadOne(self, axis):
        ret = self.axis_extra_pars[axis]['Proxy'].read_attribute("position").value
        return ret
        
    def StartOne(self, axis, position):
        self.axis_extra_pars[axis]['Proxy'].write_attribute("position", position)

    def StopOne(self, axis):
        self.axis_extra_pars[axis]['Proxy'].command_inout("stop")

    def AbortOne(self, axis):
        self.axis_extra_pars[axis]['Proxy'].command_inout("abort")

    def SetAxisPar(self, axis, name, value):
        if self.axis_extra_pars[axis]['Proxy']:
            if name == 'velocity':
                self.axis_extra_pars[axis]['Proxy'].write_attribute("velocity", value)
            elif name in ['acceleration', 'deceleration']:
                self.axis_extra_pars[axis]['Proxy'].write_attribute("acceleration", value)
            elif name == 'step_per_unit':
                self.axis_extra_pars[axis]['Proxy'].write_attribute("steps_per_unit", value)
            else:
                self._log.debug('Parameter %s is not set' % name)

    def GetAxisPar(self, axis, name):
        if self.axis_extra_pars[axis]['Proxy']:
            if name == 'velocity':
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("velocity").value
            elif name in ['acceleration', 'deceleration']:
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("acceleration").value
            elif name == 'step_per_unit':
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("steps_per_unit").value
            else:
                result = None
        else:
            result = None
        return result

    def GetAxisExtraPar(self, axis, name):
        return self.axis_extra_pars[axis][name]
    
    def SetAxisExtraPar(self, axis, name, value):
        if name == 'Tango_Device':
            self.axis_extra_pars[axis][name] = value
            try:
                self.axis_extra_pars[axis]['Proxy'] = DeviceProxy(value)
                self._log.info('axis {:d} DeviceProxy set to: {:s}'.format(axis, value))
            except Exception as e:
                self.axis_extra_pars[axis]['Proxy'] = None
                raise e

    def DefinePosition(self, axis, position):
        self.axis_extra_pars[axis]['Proxy'].command_inout("set_position", position)

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
                    self.axis_extra_pars[axis]['Proxy'].command_inout("homing_minus")
                else:
                    self.axis_extra_pars[axis]['Proxy'].command_inout("homing_plus")
            except Exception as e:
                self._log.error(e)

