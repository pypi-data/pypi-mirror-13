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
import xlrd

import strupy.units as u

from MaterialConcrete import MaterialConcrete
from MaterialRcsteel import MaterialRcsteel

class RcPanelDataLoader():

    def __init__(self):
        print "RcPanelDataLoader init"
        
    def RFEMxlsloader(self, rcpanel, rcpanelload):
        from Tkinter import Tk
        from tkFileDialog import askopenfilename
        root = Tk()
        root.withdraw()
        filename = askopenfilename(parent=root,title='Choose a file')
        #filename = '/home/lukaszlab/Dropbox/PYAPPS_STRUCT/x_mathcad/PLYTA FUND/pfund_120815.xls'
        root.destroy()
        #--opening sheets
        book = xlrd.open_workbook(filename)
        surface_sheet = book.sheet_by_name(book.sheet_names()[0])
        result_sheet = book.sheet_by_name(book.sheet_names()[1])
        #--solver deta units
        solverunit_thicknesss = u.mm
        solverunit_coord = u.m
        solverunit_moment = u.kNm
        solverunit_force = u.kN     
        #--preparing dictionary with surface number as keys
        surface_number = np.array(surface_sheet.col_values(0)[2:])
        surface_number  = np.vectorize(int)(surface_number)
        surface_thicknesss = np.array(surface_sheet.col_values(5)[2:])
        thicknesssdict = dict(zip(surface_number, surface_thicknesss))
        emptyrecord = []
        for key in thicknesssdict:
            if thicknesssdict[key] == '':
                emptyrecord.append(key)
        for i in emptyrecord:
            thicknesssdict.pop(i)
        for key in thicknesssdict:
            thicknesssdict[key] = float(thicknesssdict[key])
        #--panel properties in rcpanel
        rcpanel.surfaceID = result_sheet.col_values(0)[2:]
        for i in range(len(rcpanel.surfaceID)):
            if rcpanel.surfaceID[i] == '':
                rcpanel.surfaceID[i] = rcpanel.surfaceID[i-1]
        rcpanel.surfaceID = np.array(rcpanel.surfaceID)
        rcpanel.surfaceID  = np.vectorize(int)(rcpanel.surfaceID)
        rcpanel.coord_Xp = np.array(result_sheet.col_values(2)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        rcpanel.coord_Yp  = np.array(result_sheet.col_values(3)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        rcpanel.coord_Zp = np.array(result_sheet.col_values(4)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        rcpanel.h = np.vectorize(lambda x: thicknesssdict[x])(rcpanel.surfaceID) * (solverunit_thicknesss / rcpanel.h_unit).asNumber()
        #--panel internal forces in rcpanelload
        rcpanelload.panel = rcpanel
        rcpanelload.moment_mx= np.array(result_sheet.col_values(5)[2:]) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        rcpanelload.moment_my= np.array(result_sheet.col_values(6)[2:]) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        rcpanelload.moment_mxy= np.array(result_sheet.col_values(7)[2:]) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        rcpanelload.force_vx= np.array(result_sheet.col_values(8)[2:]) * (solverunit_force / rcpanelload.force_unit).asNumber()
        rcpanelload.force_vy= np.array(result_sheet.col_values(9)[2:]) * (solverunit_force / rcpanelload.force_unit).asNumber()
        rcpanelload.force_nx= np.array(result_sheet.col_values(10)[2:]) * (solverunit_force / rcpanelload.force_unit).asNumber()
        rcpanelload.force_ny= np.array(result_sheet.col_values(11)[2:]) * (solverunit_force / rcpanelload.force_unit).asNumber()
        rcpanelload.force_nxy= np.array(result_sheet.col_values(12)[2:]) * (solverunit_force / rcpanelload.force_unit).asNumber()
        #--calcullating equivalent internal forces in  RcPanelLoad object
        rcpanelload.calc_equivalent_load()

# Test if main
if __name__ == '__main__':
    from RcPanel import RcPanel
    from RcPanelLoad import RcPanelLoad
    panel = RcPanel()
    load = RcPanelLoad()
    loader = RcPanelDataLoader()
    panel.coord_unit = u.cm
    load.moment_unit = u.Nm
    load.force_unit = u.N
    loader.RFEMxlsloader(panel, load)
    print panel.coord_Xp * panel.coord_unit
    print load.moment_mx * load.moment_unit
    print load.force_nx * load.force_unit
    #panel.plot_coordinates()
    #panel.calculate_flatten_coordinates()
    #panel.plot_flat_shape()