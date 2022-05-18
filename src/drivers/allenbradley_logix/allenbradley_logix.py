# Simumatik Gateway - Simumatik 3rd party integration tool
# Copyright (C) 2021 Simumatik AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ..driver import driver, VariableQuality, VariableDatatype

from multiprocessing import Pipe
from typing import Optional
from pycomm3 import LogixDriver
    

class allenbradley_logix(driver):
    '''
    This driver supports services specific to ControlLogix, CompactLogix, and Micro800 PLCs.
    The driver is based on the library pycomm3: https://github.com/ottowayi/pycomm3.

    Parameters:
    ip  : String    : ip address of the PLC
    '''

    def __init__(self, name: str, pipe: Optional[Pipe] = None):
        """
        :param name: (optional) Name for the driver
        :param pipe: (optional) Pipe used to communicate with the driver thread. See gateway.py
        """
        # Inherit
        driver.__init__(self, name, pipe)
        
        self.ip = '192.168.0.1'


    def connect(self) -> bool:
        """ Connect driver.
        
        : returns: True if connection stablished False if not
        """
        # Create connection
        try:
            self._connection = LogixDriver(self.ip)
            self._connection.open()
        except Exception as e:
            self.sendDebugInfo(f"Connection with {self.ip} cannot be stablished.")
            return False

        # Check connection status.
        if self._connection.connected:
            return True
        else:
            self.sendDebugInfo(f"Driver not connected.") 
            return False


    def disconnect(self):
        """ Disconnect driver.
        """
        if self._connection:
            self._connection.close()


    def addVariables(self, variables: dict):
        """ Add variables to the driver. Correctly added variables will be added to internal dictionary 'variables'.
        Any error adding a variable should be communicated to the server using sendDebugInfo() method.
        : param variables: Variables to add in a dict following the setup format. (See documentation) 
        """
        for var_id in list(variables.keys()):
            var_data = dict(variables[var_id])
            try:
                var_data['logix_data_type'] = self._connection.get_tag_info(var_id)['data_type_name']
                var_data['value'] = None
                self.variables[var_id] = var_data 
            except Exception as e:
                self.sendDebugInfo(f'SETUP: {e} \"{var_id}\"')
                

    def readVariables(self, variables: list) -> list:
        """ Read given variable values. In case that the read is not possible or generates an error BAD quality should be returned.
        : param variables: List of variable ids to be read. 
        : returns: list of tupples including (var_id, var_value, VariableQuality)
        """
        res = []
        try:
            values = self._connection.read(*variables)
            if not isinstance(values, list):
                values = [values]
            for (tag, value, _, error) in values:
                if error:
                    res.append((tag, None, VariableQuality.BAD))
                else:
                    res.append((tag, value, VariableQuality.GOOD))
        except Exception as e:
            self.sendDebugInfo(f'exception reading variable values: {e}')
        return res


    def writeVariables(self, variables: list) -> list:
        """ Write given variable values. In case that the write is not possible or generates an error BAD quality should be returned.
        : param variables: List of tupples with variable ids and the values to be written (var_id, var_value). 
        : returns: list of tupples including (var_id, var_value, VariableQuality)
        """
        res = []

        # Mismatch if value is defined as BYTE (or Word) in simumatik and SINT (or Int) in RSLogix 5000
        for count, (var_id, var_value) in enumerate(variables):
            if self.variables[var_id]['logix_data_type'] == 'SINT' and self.variables[var_id]['datatype'] == VariableDatatype.BYTE:
                while var_value > 127: 
                    var_value -= 255
                
                variables[count] = (var_id, var_value)

            if self.variables[var_id]['logix_data_type'] == 'INT' and self.variables[var_id]['datatype'] == VariableDatatype.WORD:
                while var_value > 32767: 
                    var_value -= 65536
                
                variables[count] = (var_id, var_value)

        try:
            values = self._connection.write(*variables)
            if not isinstance(values, list):
                values = [values]
            for (tag, value, _, error) in values:
                if error:
                    res.append((tag, value, VariableQuality.BAD))
                else:
                    res.append((tag, value, VariableQuality.GOOD))
        except Exception as e:
            self.sendDebugInfo(f'exception writing variable values: {e}')

        return res