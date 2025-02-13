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

import sys
from os import path
import time
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from drivers.plcsim.plcsim import plcsim
from drivers.driver import VariableOperation, VariableDatatype

VARIABLES = {
    'IB0':{'datatype': VariableDatatype.BYTE, 'size': 1, 'operation': VariableOperation.WRITE},
    'QB0':{'datatype': VariableDatatype.BYTE, 'size': 1, 'operation': VariableOperation.READ},
    #'I1.2':{'datatype': VariableDatatype.BOOL, 'size': 1, 'operation': VariableOperation.WRITE},
    #'Q1.2':{'datatype': VariableDatatype.BOOL, 'size': 1, 'operation': VariableOperation.READ},
    #'IW2':{'datatype': VariableDatatype.WORD, 'size': 1, 'operation': VariableOperation.WRITE},
    #'QW2':{'datatype': VariableDatatype.WORD, 'size': 1, 'operation': VariableOperation.READ},
    #'IW4':{'datatype': VariableDatatype.INTEGER, 'size': 1, 'operation': VariableOperation.WRITE},
    #'QW4':{'datatype': VariableDatatype.INTEGER, 'size': 1, 'operation': VariableOperation.READ},
    #'ID10':{'datatype': VariableDatatype.DWORD, 'size': 1, 'operation': VariableOperation.WRITE},
    #'QD10':{'datatype': VariableDatatype.DWORD, 'size': 1, 'operation': VariableOperation.READ},
    #'ID14':{'datatype': VariableDatatype.INTEGER, 'size': 1, 'operation': VariableOperation.WRITE},
    #'QD14':{'datatype': VariableDatatype.INTEGER, 'size': 1, 'operation': VariableOperation.READ},
    #'ID18':{'datatype': VariableDatatype.FLOAT, 'size': 1, 'operation': VariableOperation.WRITE},
    #'QD18':{'datatype': VariableDatatype.FLOAT, 'size': 1, 'operation': VariableOperation.READ},
    }

d = plcsim(None, 'test')
d.ip = '192.168.0.1'
d.rack = 0
d.slot = 1
#d.mode = 'TIA'

if d.connect():
    d.addVariables(VARIABLES)

    counter = 0
    t = time.perf_counter()
    while time.perf_counter()-t < 10:

        print(d.readVariables(['QB0']), counter)
        d.writeVariables([('IB0', counter%256)])
        counter += 1

    d.disconnect()
