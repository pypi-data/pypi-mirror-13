'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2016-02-21

This file is part of StruPy.
StruPy is a structural engineering design Ptequmython package.
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
- RFEMxlsloader() upgraded
File version 0.3 changes:
- RFEMxlsloader() upgraded for RFEM 5 output file
'''

import numpy as np
import xlrd

import strupy.units as u

class RcPanelDataLoader():

    def __init__(self):
        print "RcPanelDataLoader init"
        
    def RFEMxlsloader(self, rcpanel, rcpanelload, progress=None):
        #--loading xls files and recognizing surface/result sheets
        from Tkinter import Tk
        from tkFileDialog import askopenfilename
        surface_sheet = None
        result_sheet = None
        tryNumber = 1
        while not (surface_sheet and result_sheet):
            root = Tk()
            root.withdraw()
            #----
            ask_text = 'Choose'
            if not surface_sheet:
                ask_text += ' [surface]'
            if not result_sheet:
                ask_text += ' [result]' 
            ask_text += ' xls Rfem output file'
            #----
            filename = askopenfilename(parent=root,title=ask_text, filetypes=[('xls file', '*.xls')])
            book = xlrd.open_workbook(filename)
            for i in book.sheet_names():
                if '1.4' in i:
                    surface_sheet = book.sheet_by_name(i) #<<<<<<<< surface_sheet
                if ('Surfaces - Base' in i) or ('Surfaces - Basic' in i) or ('Powierzchnie - Podst' in i)  :
                    result_sheet = book.sheet_by_name(i) #<<<<<<<< result_sheet
            if tryNumber == 4:
                return 0
            tryNumber +=1
        root.destroy()
        #----function for finding column number with some text
        def find_column(headerTextlist, sheet, row):
            find_result = None
            for i in range(40):
                for text in headerTextlist:
                    try:
                        if text == str(sheet.col_values(i)[row].encode('cp1250')):
                            find_result = [i, str(sheet.col_values(i)[row].encode('cp1250'))]
                    except IndexError:
                        pass
            if not find_result:
                find_result = ['Not found', None]
            return find_result
        #----
        if progress:
            progress.setValue(20)
        #--finding solver data units
        #----thicknesss unit
        header = find_column(['d [mm]', 'd [cm]', 'd [m]'], surface_sheet, 1)[1]
        print header 
        if '[mm]' in header:
            solverunit_thicknesss = u.mm
        elif '[cm]' in header:
            solverunit_thicknesss = u.cm
        elif '[m]' in header:
            solverunit_thicknesss = u.m
        else :
            solverunit_thicknesss = None
        #----coordinate unit   
        header = find_column([  'Grid Point Coordinates [m]',
                                'Grid Point Coordinates [cm]', 
                                'Grid Point Coordinates [mm]',
                                'Wsp\xf3\xb3rz\xeadne punkt\xf3w rastru [m]',
                                'Wsp\xf3\xb3rz\xeadne punkt\xf3w rastru [cm]',
                                'Wsp\xf3\xb3rz\xeadne punkt\xf3w rastru [mm]'], result_sheet, 0)[1]
        print header
        if 'mm' in header:
            solverunit_coord = u.m
        elif 'cm' in header:
            solverunit_coord = u.cm
        elif 'm' in header:
            solverunit_coord = u.m
        else :
            solverunit_coord = None      
        #----internale forces moment unit
        header = find_column([  'Moments [Nm/m]',
                                'Moments [kNm/m]',
                                'Momenty [Nm/m]',
                                'Momenty [kNm/m]'], result_sheet, 0)[1]
        if '[Nm/m]' in header:
            solverunit_moment = u.Nm
        elif '[kNm/m]' in header:
            solverunit_moment = u.kNm
        else :
            solverunit_moment = None      
        #----internale forces force unit
        print result_sheet.col_values(10)[0].encode('cp1250')
        header = find_column([  'Axial Forces [N/m]',
                                'Axial Forces [kN/m]',
                                'Si\xb3y osiowe [N/m]',
                                'Si\xb3y osiowe [kN/m]'], result_sheet, 0)[1]
        if '[N/m]' in header:
            solverunit_force = u.N
        elif '[kN/m]' in header:
            solverunit_force = u.kN
        else :
            solverunit_force = None      
        #--preparing dictionary with surface number as keys
        col_surface_number = find_column(['No.', 'nr'], result_sheet, 1)[0]
        surface_number = np.array(surface_sheet.col_values(col_surface_number)[2:])
        surface_number  = np.vectorize(int)(surface_number)
        col_surface_thicknesss = find_column(['d [mm]', 'd [cm]', 'd [m]'], surface_sheet, 1)[0]
        surface_thicknesss = np.array(surface_sheet.col_values(col_surface_thicknesss)[2:])
        thicknesssdict = dict(zip(surface_number, surface_thicknesss))
        emptyrecord = []
        for key in thicknesssdict:
            if thicknesssdict[key] == '':
                emptyrecord.append(key)
        for i in emptyrecord:
            thicknesssdict.pop(i)
        for key in thicknesssdict:
            thicknesssdict[key] = float(thicknesssdict[key])
        #----
        if progress:
            progress.setValue(40)
        #--panel properties in rcpanel
        col_surfaceID = find_column(['No.', 'nr'], result_sheet, 1)[0]
        rcpanel.surfaceID = result_sheet.col_values(col_surfaceID)[2:]
        for i in range(len(rcpanel.surfaceID)):
            if rcpanel.surfaceID[i] == '':
                rcpanel.surfaceID[i] = rcpanel.surfaceID[i-1]
        rcpanel.surfaceID = np.array(rcpanel.surfaceID)
        rcpanel.surfaceID  = np.vectorize(int)(rcpanel.surfaceID)
        col_coord_Xp = find_column(['X'], result_sheet, 1)[0]
        print col_coord_Xp
        rcpanel.coord_Xp = np.array(result_sheet.col_values(col_coord_Xp)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        col_coord_Yp = find_column(['Y'], result_sheet, 1)[0]
        rcpanel.coord_Yp  = np.array(result_sheet.col_values(col_coord_Yp)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        col_coord_Zp = find_column(['Z'], result_sheet, 1)[0]
        rcpanel.coord_Zp = np.array(result_sheet.col_values(col_coord_Zp)[2:]) * (solverunit_coord / rcpanel.coord_unit).asNumber()
        rcpanel.h = np.vectorize(lambda x: thicknesssdict[x])(rcpanel.surfaceID) * (solverunit_thicknesss / rcpanel.h_unit).asNumber()
        #--unexpected value detect and replace in result data from RFEM
        def unexpected_replace(value):
            if value == '-':
                value = 0.0
            return float(value)
        #--panel internal forces in rcpanelload
        col_moment_mx = find_column(['mx'], result_sheet, 1)[0]
        moment_mx = result_sheet.col_values(col_moment_mx)[2:]
        moment_mx = np.vectorize(unexpected_replace)(moment_mx)
        rcpanelload.moment_mx= np.array(moment_mx) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        moment_mx = []
        #----
        col_moment_my = find_column(['my'], result_sheet, 1)[0]
        moment_my = result_sheet.col_values(col_moment_my)[2:]
        moment_my = np.vectorize(unexpected_replace)(moment_my)      
        rcpanelload.moment_my= np.array(moment_my) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        moment_my = []
        #----
        col_moment_mxy = find_column(['mxy'], result_sheet, 1)[0]
        moment_mxy = result_sheet.col_values(col_moment_mxy)[2:]
        moment_mxy = np.vectorize(unexpected_replace)(moment_mxy)
        rcpanelload.moment_mxy= np.array(moment_mxy) * (solverunit_moment / rcpanelload.moment_unit).asNumber()
        moment_mxy = []
        #----
        col_force_vx = find_column(['vx'], result_sheet, 1)[0]
        force_vx = result_sheet.col_values(col_force_vx)[2:]
        force_vx = np.vectorize(unexpected_replace)(force_vx)
        rcpanelload.force_vx= np.array(force_vx) * (solverunit_force / rcpanelload.force_unit).asNumber()
        force_vx = []
        #----
        col_force_vy = find_column(['vy'], result_sheet, 1)[0]
        force_vy = result_sheet.col_values(col_force_vy)[2:]
        force_vy = np.vectorize(unexpected_replace)(force_vy)
        rcpanelload.force_vy= np.array(force_vy) * (solverunit_force / rcpanelload.force_unit).asNumber()
        force_vy = []
        #----
        col_force_nx = find_column(['nx'], result_sheet, 1)[0]
        force_nx = result_sheet.col_values(col_force_nx)[2:]
        force_nx = np.vectorize(unexpected_replace)(force_nx)
        rcpanelload.force_nx= np.array(force_nx) * (solverunit_force / rcpanelload.force_unit).asNumber()
        force_nx = []
        #----
        col_force_ny = find_column(['ny'], result_sheet, 1)[0]
        force_ny = result_sheet.col_values(col_force_ny)[2:]
        force_ny = np.vectorize(unexpected_replace)(force_ny)
        rcpanelload.force_ny= np.array(force_ny) * (solverunit_force / rcpanelload.force_unit).asNumber()
        force_ny = []
        #----
        col_force_nxy = find_column(['nxy'], result_sheet, 1)[0]
        force_nxy = result_sheet.col_values(col_force_nxy)[2:]
        force_nxy = np.vectorize(unexpected_replace)(force_nxy)
        rcpanelload.force_nxy= np.array(force_nxy) * (solverunit_force / rcpanelload.force_unit).asNumber()
        force_nxy = []
        #----
        if progress:
            progress.setValue(80)
        #--calcullating equivalent internal forces in  RcPanelLoad object
        rcpanelload.calc_equivalent_load()
        #----
        if progress:
            progress.setValue(0)

# Test if main
if __name__ == '__main__':
    from RcPanel import RcPanel
    from RcPanelLoad import RcPanelLoad
    panel = RcPanel()
    load = RcPanelLoad()
    loader = RcPanelDataLoader()
    panel.coord_unit = u.cm
    load.moment_unit = u.kNm
    load.force_unit = u.kN
    loader.RFEMxlsloader(panel, load)
    print panel.coord_Xp * panel.coord_unit
    print load.moment_mx * load.moment_unit
    print load.moment_my * load.moment_unit
    print load.moment_mxy * load.moment_unit
    print load.force_nx * load.force_unit
    