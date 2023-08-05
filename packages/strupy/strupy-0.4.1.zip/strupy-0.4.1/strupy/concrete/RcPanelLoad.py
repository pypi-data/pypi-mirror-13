'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2016-01-13

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
- xxxx
'''
import numpy as np

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcPanelLoad(MaterialConcrete, MaterialRcsteel):

    def __init__(self):
        print "RcPanelLoad init"
        #----
        self.panel = 'Noname'
        #----
        self.moment_mx= np.array([]) * u.kNm
        self.moment_my= np.array([]) * u.kNm
        self.moment_mxy= np.array([]) * u.kNm
        self.force_nx= np.array([]) * u.kNm
        self.force_ny= np.array([]) * u.kNm
        self.force_nxy= np.array([]) * u.kNm
        self.force_vx= np.array([]) * u.kNm
        self.force_vy= np.array([]) * u.kNm
        #----
        self.moment_equ_MX= np.array([]) * u.kNm
        self.moment_equ_MY= np.array([]) * u.kNm
        self.force_equ_NX= np.array([]) * u.kNm
        self.force_equ_NY= np.array([]) * u.kNm
        self.force_unit = u.kN
        self.moment_unit = u.kN

    def calc_equivalent_load(self):
        print 'start'
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
        print 'koniec'

    def __plot(self, values, unit, title):
        import matplotlib.pyplot as plt
        lenunit = u.m
        plt.scatter(self.panel.coord_flatten_x, self.panel.coord_flatten_y, c=u.xunumlistvalue(values, unit), marker='.', edgecolors='none', s=100)
        plt.colorbar()
        plt.axes().set_aspect('equal', 'datalim')
        plt.title(title + ' * ' + str(unit))
        plt.show()
        
    def plot_mx(self):
        self.__plot(self.moment_mx, self.moment_unit, 'mx')

    def plot_my(self):
        self.__plot(self.moment_my, self.moment_unit, 'my')
        
    def plot_mxy(self):
        self.__plot(self.moment_mxy, self.moment_unit, 'mxy')

    def plot_equ_MX(self):
        self.__plot(self.moment_equ_MX, self.moment_unit, 'equ_MX')

    def plot_equ_MY(self):
        self.__plot(self.moment_equ_MY, self.moment_unit, 'equ_MY')

    def plot_nx(self):
        self.__plot(self.force_nx, self.force_unit, 'nx')
        
    def plot_ny(self):
        self.__plot(self.force_ny, self.force_unit, 'ny')
        
    def plot_nxy(self):
        self.__plot(self.force_nxy, self.force_unit, 'nxy')

    def plot_equ_NX(self):
        self.__plot(self.force_equ_NX, self.force_unit, 'equ_NX')

    def plot_equ_NY(self):
        self.__plot(self.force_equ_NY, self.force_unit, 'equ_NY')
        
# Test if main
if __name__ == '__main__':
    load = RcPanelLoad()

    