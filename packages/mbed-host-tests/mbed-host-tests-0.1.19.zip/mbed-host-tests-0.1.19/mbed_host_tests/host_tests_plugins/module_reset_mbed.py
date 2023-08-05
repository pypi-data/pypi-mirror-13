"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

from host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_Mbed(HostTestPluginBase):

    def safe_sendBreak(self, serial):
        """! Wraps serial.sendBreak() to avoid serial::serialposix.py exception on Linux
        @details  Traceback (most recent call last):
                    File "make.py", line 189, in <module>
                      serial.sendBreak()
                    File "/usr/lib/python2.7/dist-packages/serial/serialposix.py", line 511, in sendBreak
                      termios.tcsendbreak(self.fd, int(duration/0.25))
                  error: (32, 'Broken pipe')

        @return Returns True if command was successful
        """
        result = True
        try:
            serial.sendBreak()
        except:
            # In linux a termios.error is raised in sendBreak and in setBreak.
            # The following setBreak() is needed to release the reset signal on the target mcu.
            try:
                serial.setBreak(False)
            except:
                result = False
        return result

    # Plugin interface
    name = 'HostTestPluginResetMethod_Mbed'
    type = 'ResetMethod'
    stable = True
    capabilities = ['default']
    required_parameters = ['serial']

    def setup(self, *args, **kwargs):
        """! Configure plugin, this function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments
        @details Each capability e.g. may directly just call some command line program or execute building pythonic function
        @return Capability call return value
        """
        if not kwargs['serial']:
            self.print_plugin_error("Error: serial port not set (not opened?)")
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if kwargs['serial']:
                if capability == 'default':
                    serial = kwargs['serial']
                    result = self.safe_sendBreak(serial)
        return result


def load_plugin():
    """! Returns plugin available in this module
    """
    return HostTestPluginResetMethod_Mbed()
