'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2016-02-10

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://strupy.org/

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.2 changes:
- RcPanelLoad class upgraded
'''
import numpy as np

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcPanelLoad(MaterialConcrete, MaterialRcsteel):

    def __init__(self):
        print "RcPanelLoad init"
        #----
        self.moment_mx= np.array([])
        self.moment_my= np.array([])
        self.moment_mxy= np.array([])
        self.force_nx= np.array([])
        self.force_ny= np.array([])
        self.force_nxy= np.array([])
        self.force_vx= np.array([])
        self.force_vy= np.array([])
        #----
        self.moment_equ_MX= np.array([])
        self.moment_equ_MY= np.array([])
        self.force_equ_NX= np.array([])
        self.force_equ_NY= np.array([])
        #----
        self.force_unit = u.kN
        self.moment_unit = u.kNm

    def calc_equivalent_load(self):
        def equ_M (MN, MT):
            Mp = MN + abs(MT)
            Mn = MN - abs(MT) 
            if abs(Mp) >= abs(Mn):
                return Mp
            if abs(Mn) > abs(Mp):
                return Mn
        def equ_N (NN, NV):
            Nt = NN + abs(NV)
            Nc = NN - abs(NV)
            if Nt > 0:
                return Nt
            else:
                return Nc
        self.moment_equ_MX = np.vectorize(equ_M)(self.moment_mx, self.moment_mxy)
        self.moment_equ_MY = np.vectorize(equ_M)(self.moment_my, self.moment_mxy)
        self.force_equ_NX = np.vectorize(equ_N)(self.force_nx, self.force_nxy)
        self.force_equ_NY = np.vectorize(equ_N)(self.force_ny, self.force_nxy)
        
    def clear_arrays_data(self):
        self.moment_mx= np.array([])
        self.moment_my= np.array([])
        self.moment_mxy= np.array([])
        self.force_nx= np.array([])
        self.force_ny= np.array([])
        self.force_nxy= np.array([])
        self.force_vx= np.array([])
        self.force_vy= np.array([])
        #----
        self.moment_equ_MX= np.array([])
        self.moment_equ_MY= np.array([])
        self.force_equ_NX= np.array([])
        self.force_equ_NY= np.array([])
       
# Test if main
if __name__ == '__main__':
    load = RcPanelLoad()
    