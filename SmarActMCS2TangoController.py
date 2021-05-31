from PyTango import DeviceProxy

from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Access, Description, DataAccess


class SmarActMCS2TangoController(MotorController):
    MaxDevice = 99

    axis_attributes = {
        'Tango_Device': {
            Type: str,
            Description: 'The Tango Device'
            ' (e.g. domain/family/member)',
            Access: DataAccess.ReadWrite
        },
        'MoveMode': {
            Type: int,
            Description: 'MoveMode setting'
            '0 = absolute, 1 = relative 2-4 = ??, higher value not valid.',
            Access: DataAccess.ReadWrite
        },
        'StepFrequency': {
            Type: int,
            Description: 'StepFrequency setting'
            'Default = 1000',
            Access: DataAccess.ReadWrite
        },
    }

    def __init__(self, inst, props, *args, **kwargs):
        super(SmarActMCS2TangoController, self).__init__(
                inst, props, *args, **kwargs)

        self._log.info('Initialized')
        # do some initialization
        self.axis_extra_pars = {}

    def AddDevice(self, axis):
        self._log.info('adding axis {:d}'.format(axis))
        self.axis_extra_pars[axis] = {}
        self.axis_extra_pars[axis]['Proxy'] = None
        self.axis_extra_pars[axis]['target_position'] = 0

    def DeleteDevice(self, axis):
        self._log.info('delete axis {:d}'.format(axis))
        del self.axis_extra_pars[axis]

    def StateOne(self, axis):
        state = self.axis_extra_pars[axis]['Proxy'].command_inout("State")
        status = self.axis_extra_pars[axis]['Proxy'].command_inout("Status")
        target_position = self.axis_extra_pars[axis]['target_position']
        switch_state = MotorController.NoLimitSwitch

        if 'endstop' in status:
            if self.axis_extra_pars[axis]['Proxy'].read_attribute("position").value \
                    > target_position:
                switch_state |= MotorController.LowerLimitSwitch
            else:
                switch_state |= MotorController.UpperLimitSwitch

        return state, status, switch_state

    def ReadOne(self, axis):
        ret = self.axis_extra_pars[axis]['Proxy'].read_attribute("position").value
        return ret

    def StartOne(self, axis, position):
        self.axis_extra_pars[axis]['target_position'] = position
        self.axis_extra_pars[axis]['Proxy'].write_attribute("position", position)

    def StopOne(self, axis):
        self.axis_extra_pars[axis]['Proxy'].command_inout("stop")

    def AbortOne(self, axis):
        self.axis_extra_pars[axis]['Proxy'].command_inout("abort")

    def SetAxisPar(self, axis, name, value):
        if self.axis_extra_pars[axis]['Proxy']:
            if name == 'velocity':
                self.axis_extra_pars[axis]['Proxy'].write_attribute("Speed", value)
            elif name in ['acceleration', 'deceleration']:
                self.axis_extra_pars[axis]['Proxy'].write_attribute("Acceleration", value)
            elif name == 'step_per_unit':
                self.axis_extra_pars[axis]['Proxy'].write_attribute("Conversion", value)
            else:
                self._log.debug('Parameter %s is not set' % name)

    def GetAxisPar(self, axis, name):
        if self.axis_extra_pars[axis]['Proxy']:
            if name == 'velocity':
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("Speed").value
            elif name in ['acceleration', 'deceleration']:
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("Acceleration").value
            elif name == 'step_per_unit':
                result = self.axis_extra_pars[axis]['Proxy'].read_attribute("Conversion").value
            else:
                result = None
        else:
            result = None
        return result

    def SetAxisExtraPar(self, axis, name, value):
        if name == 'Tango_Device':
            self.axis_extra_pars[axis][name] = value
            try:
                self.axis_extra_pars[axis]['Proxy'] = DeviceProxy(value)
                self._log.info('axis {:d} DeviceProxy set to: {:s}'.format(axis, value))
            except Exception as e:
                self.axis_extra_pars[axis]['Proxy'] = None
                raise e
        elif name == 'MoveMode':
            result = self.axis_extra_pars[axis]['Proxy'].write_attribute("MoveMode", value)
        elif name == 'StepFrequency':
            result = self.axis_extra_pars[axis]['Proxy'].write_attribute("StepFrequency", value)
        else:
            result = None

    def GetAxisExtraPar(self, axis, name):
        if name == 'MoveMode':
            result = self.axis_extra_pars[axis]['Proxy'].read_attribute("MoveMode").value
        elif name == 'StepFrequency':
            result = self.axis_extra_pars[axis]['Proxy'].read_attribute("StepFrequency").value
        else:
            result = None
        return result

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
                if len(args) == 1:
                    axis = int(args[0])
                else:
                    raise ValueError('Invalid number of arguments')
            except Exception as e:
                self._log.error(e)

            self._log.info('Starting homing for axis {:d}'.format(axis))
            try:
                self.axis_extra_pars[axis]['Proxy'].command_inout("Home")
            except Exception as e:
                self._log.error(e)

