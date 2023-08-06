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
File version 0.x changes:
- xxx
'''
import numpy as np

import strupy.units as u

class RcPanelViewer():
    
    def __init__(self):
        print "RcPanelViewer"
        #----obiect to assign
        self.Panel = 'Noname'
        self.PanelLoad = 'Noname'
        #----color scale for map function
        self.colorscale = ['silver', 'yellow', 'green', 'cyan', 'purple', 'blue', 'red', 'brown', 'black']
        
    def assignPanelObiect(self, someRcPanel):
        self.Panel = someRcPanel

    def assignPanelLoadObiect(self, someRcPanelLoad):
        self.PanelLoad = someRcPanelLoad
        
    #----assigned RcPanel obiect data plot
    def plot_thickness(self):
        self.__plot(self.Panel.h, self.Panel.h_unit, 'Panel thickness')
        
    def plot_reinforcement_Anx(self):
        self.__plot(self.Panel.Anx, self.Panel.A_unit, 'Anx reinforcement')

    def plot_reinforcement_Apx(self):
        self.__plot(self.Panel.Apx, self.Panel.A_unit, 'Apx reinforcement')

    def plot_reinforcement_Any(self):
        self.__plot(self.Panel.Any, self.Panel.A_unit, 'Any reinforcement')

    def plot_reinforcement_Apy(self):
        self.__plot(self.Panel.Apy, self.Panel.A_unit, 'Apy reinforcement')
        
    def plot_rysx(self):
        self.__plot(self.Panel.rysx, u.m/u.m, 'rysx')

    def plot_rysy(self):
        self.__plot(self.Panel.rysy, u.m/u.m, 'rysy')

    def plot_mimosx(self):
        self.__plot(self.Panel.mimosx, u.m/u.m, 'mimosx')

    def plot_mimosy(self):
        self.__plot(self.Panel.mimosy, u.m/u.m, 'mimosy')
        
    def plot_ksieffx(self):
        self.__plot(self.Panel.ksieffx, u.m/u.m, 'ksieffx')

    def plot_ksieffy(self):
        self.__plot(self.Panel.ksieffy, u.m/u.m, 'ksieffy')
  
    def map_reinforcement_Anx(self):
        self.__map(self.Panel.Anx, self.Panel.A_unit, self.Panel.Anscale, 'Anx map')

    def map_reinforcement_Apx(self):
        self.__map(self.Panel.Apx, self.Panel.A_unit, self.Panel.Apscale, 'Apx map')

    def map_reinforcement_Any(self):
        self.__map(self.Panel.Any, self.Panel.A_unit, self.Panel.Anscale, 'Any map')

    def map_reinforcement_Apy(self):
        self.__map(self.Panel.Apy, self.Panel.A_unit, self.Panel.Apscale, 'Apy map')
        
    #----assigned RcPanelLoad obiect data plot
    def plot_mx(self):
        self.__plot(self.PanelLoad.moment_mx, self.PanelLoad.moment_unit, 'mx')

    def plot_my(self):
        self.__plot(self.PanelLoad.moment_my, self.PanelLoad.moment_unit, 'my')
        
    def plot_mxy(self):
        self.__plot(self.PanelLoad.moment_mxy, self.PanelLoad.moment_unit, 'mxy')

    def plot_equ_MX(self):
        self.__plot(self.PanelLoad.moment_equ_MX, self.PanelLoad.moment_unit, 'equ_MX')

    def plot_equ_MY(self):
        self.__plot(self.PanelLoad.moment_equ_MY, self.PanelLoad.moment_unit, 'equ_MY')

    def plot_nx(self):
        self.__plot(self.PanelLoad.force_nx, self.PanelLoad.force_unit, 'nx')
        
    def plot_ny(self):
        self.__plot(self.PanelLoad.force_ny, self.PanelLoad.force_unit, 'ny')
        
    def plot_nxy(self):
        self.__plot(self.PanelLoad.force_nxy, self.PanelLoad.force_unit, 'nxy')

    def plot_equ_NX(self):
        self.__plot(self.PanelLoad.force_equ_NX, self.PanelLoad.force_unit, 'equ_NX')

    def plot_equ_NY(self):
        self.__plot(self.PanelLoad.force_equ_NY, self.PanelLoad.force_unit, 'equ_NY')
        
    #----plot functions    
    def __plot(self, values, unit, title):
        import matplotlib.pyplot as plt
        lenunit = self.Panel.h_unit
        x = self.Panel.coord_flatten_x
        y = self.Panel.coord_flatten_y
        colors = values
        #----if all values the same, diferent for colorscale is needed
        if np.max(colors) == np.max(colors):
            colors[0] = np.min(values) * 1.01
            colors[1] = np.min(values) * 0.99
        #----
        plt.scatter(x, y, c=colors, marker='.', edgecolors='none', s=100)
        plt.colorbar()
        plt.axes().set_aspect('equal', 'datalim')
        plt.title(title + ' x ' + str(unit))
        plt.show()
        
    def plot_coordinates(self):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.Panel.coord_Xp, self.Panel.coord_Yp, self.Panel.coord_Zp, c='red', marker='.')
        ax.set_xlabel('X *' + str(self.Panel.coord_unit))
        ax.set_ylabel('Y *' + str(self.Panel.coord_unit))
        ax.set_zlabel('Z *' + str(self.Panel.coord_unit))
        plt.title('panel points coordinates')
        plt.show()
        
    def plot_flatten_shape(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(self.Panel.coord_flatten_x,self.Panel.coord_flatten_y, c='red', marker='.', edgecolors='none', s=100)
        ax.set_xlabel('X *' + str(self.Panel.coord_unit))
        ax.set_ylabel('Y *' + str(self.Panel.coord_unit))
        plt.axes().set_aspect('equal', 'datalim')
        plt.title('panel flat view')
        plt.show()
        #fig.savefig('temp.png', dpi=fig.dpi)
        
    def __ValueToColor(self, value = 1.1, valuescalelist = np.array([2, 6, 7, 10, 16, 17, 18, float('inf'), float('inf')])):
        i = 0
        while (value > valuescalelist[i]):
            i += 1
        if valuescalelist[i] == float('inf'):
            i = len(valuescalelist) - 1
        return self.colorscale[i]
    
    def __map(self, values = np.array([1, 3]), unit=u.cm, valuescalelist = np.array([1, 5, 7, float('inf')]) , title = 'Noname'):
        #----
        self.Panel.Ascale_sort()
        #----
        import matplotlib.pyplot as plt
        from matplotlib.colors import cnames
        lenunit = u.m
        x = self.Panel.coord_flatten_x
        y = self.Panel.coord_flatten_y
        color = np.vectorize(lambda x: self.__ValueToColor(x, valuescalelist))(values)
        color = np.vectorize(lambda x: cnames[x])(color)
        plt.scatter(x, y, c=color, marker='.', edgecolors='none', s=100, label=[2])
        plt.axes().set_aspect('equal', 'datalim')
        plt.title(title + 'x ' + str(unit))
        #----legend
        import matplotlib.patches as mpatches
        legend_texts = valuescalelist
        legend_colors = np.vectorize(lambda x: cnames[x])(self.colorscale)
        legend_recs = []
        for i in range(0,len(legend_colors)):
            legend_recs.append(mpatches.Rectangle((0,0),1,1,fc=legend_colors[i]))
        plt.legend(legend_recs,legend_texts,loc=4)
        plt.legend(legend_recs,legend_texts,loc=2)
        #----
        plt.show()
    
# Test if main
if __name__ == '__main__':
    print ('test RcPanelViewer')
    viewer = RcPanelViewer()
    print viewer.colorscale
    print viewer._RcPanelViewer__ValueToColor(1000)