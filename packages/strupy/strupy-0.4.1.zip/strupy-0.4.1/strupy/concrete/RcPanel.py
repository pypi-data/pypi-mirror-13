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
import copy

import numpy as np

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcPanel(MaterialConcrete, MaterialRcsteel):

    def __init__(self):
        print "RcPanel init"
        MaterialConcrete.__init__(self)
        MaterialRcsteel.__init__(self)
        #----
        self.surfaceID = np.array([])
        #----
        self.h = np.array([])
        self.h_unit = u.cm
        #----
        self.coord_Xp = np.array([])
        self.coord_Yp = np.array([])
        self.coord_Zp = np.array([])
        self.coord_flatten_x = np.array([])
        self.coord_flatten_y = np.array([])
        self.coord_unit = u.m
        #self.transf_matrix = np.array([[1,0,0], [0,1,0]])
        #----
        self.ap=5.0*u.cm
        self.an=5.0*u.cm
        self.fip=20.0*u.mm
        self.fin=20.0*u.mm
        self.rysAp=1.0
        self.rysAn=1.0
        self.wlimp=0.3*u.mm
        self.wlimn=0.3*u.mm
        #----
        self.Apx= np.array([])
        self.Anx= np.array([])
        self.Apy= np.array([])
        self.Any= np.array([])
        self.A_unit = u.cm2
        #----
        self.rysx= np.array([])
        self.rysy= np.array([])  
        self.mimosx= np.array([])
        self.mimosy= np.array([]) 
        self.ksieffx= np.array([])
        self.ksieffy= np.array([])  
    def set_pointXcoordinates(self, Xcoordinates):
        self.coord_Xp = Xcoordinates

    def set_pointYcoordinates(self, Ycoordinates):
        self.coord_Yp = Ycoordinates

    def set_pointZcoordinates(self, Zcoordinates):
        self.coord_Zp = Zcoordinates
        
    def set_pointThickness(self, Thickness):
        self.h = Thickness
        
    def calculate_flatten_coordinates(self):
        self.coord_flatten_x = self.coord_Xp
        self.coord_flatten_y = self.coord_Yp    
        
    def plot_coordinates(self):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.coord_Xp, self.coord_Yp, self.coord_Zp, c='red', marker='.')
        ax.set_xlabel('X *' + str(self.coord_unit))
        ax.set_ylabel('Y *' + str(self.coord_unit))
        ax.set_zlabel('Z *' + str(self.coord_unit))
        #plt.axes().set_aspect('equal')
        plt.title('panel points coordinates')
        plt.show()
        
    def plot_flat_shape(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(self.coord_flatten_x,self.coord_flatten_y, c='red', marker='.', edgecolors='none', s=100)
        ax.set_xlabel('X *' + str(self.coord_unit))
        ax.set_ylabel('Y *' + str(self.coord_unit))
        plt.axes().set_aspect('equal', 'datalim')
        plt.title('panel flat view')
        plt.show()
        fig.savefig('temp.png', dpi=fig.dpi)
        
    def plot_thickness(self):
        self.__plot(self.h, u.cm, 'Panel thickness')
        
    def plot_reinforcement_Anx(self):
        self.__plot(self.Anx, u.cm2, 'Anx reinforcement')

    def plot_reinforcement_Apx(self):
        self.__plot(self.Apx, u.cm2, 'Apx reinforcement')

    def plot_reinforcement_Any(self):
        self.__plot(self.Any, u.cm2, 'Any reinforcement')

    def plot_reinforcement_Apy(self):
        self.__plot(self.Apy, u.cm2, 'Apy reinforcement')
        
    def plot_rysx(self):
        self.__plot(self.rysx * u.m/u.m, u.m/u.m, 'rysx')

    def plot_rysy(self):
        self.__plot(self.rysy * u.m/u.m, u.m/u.m, 'rysy')

    def plot_mimosx(self):
        self.__plot(self.mimosx * u.m/u.m, u.m/u.m, 'mimosx')

    def plot_mimosy(self):
        self.__plot(self.mimosy * u.m/u.m, u.m/u.m, 'mimosy')
        
    def plot_ksieffx(self):
        self.__plot(self.ksieffx * u.m/u.m, u.m/u.m, 'ksieffx')

    def plot_ksieffy(self):
        self.__plot(self.ksieffy * u.m/u.m, u.m/u.m, 'ksieffy')

    def __plot(self, values, unit, title):
        import matplotlib.pyplot as plt
        lenunit = u.m
        plt.scatter(self.coord_flatten_x, self.coord_flatten_y, c=u.xunumlistvalue(values, unit), marker='.', edgecolors='none', s=100)
        plt.colorbar()
        plt.axes().set_aspect('equal', 'datalim')
        plt.title(title + 'x ' + str(unit))
        plt.show()
        #plt.savefig('temp.png', dpi=80)

# Test if main
if __name__ == '__main__':

    print ('test RcPanel')
    panel=RcPanel()
    
    xi = []
    yi = []
    zi = []
    
    for x in range(34):
        for y in range (23):
            xi.append(float(x))
            yi.append(float(y))
            zi.append(float(1))
    
    panel.set_pointXcoordinates(np.array(xi))
    print panel.coord_Xp
    panel.set_pointYcoordinates(np.array(yi))
    print panel.coord_Yp
    panel.set_pointZcoordinates(np.array(zi))
    print panel.coord_Zp
    panel.set_pointThickness(np.array([100, 100, 100, 100, 100, 100, 100, 100]))
    print panel.h
    panel.plot_coordinates()
    panel.calculate_flatten_coordinates()
    panel.plot_flat_shape()

    