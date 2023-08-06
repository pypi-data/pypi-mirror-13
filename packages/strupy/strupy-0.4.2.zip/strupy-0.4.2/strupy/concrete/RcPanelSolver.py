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
- RcPanelSolver class upgraded
'''
import numpy as np

import strupy.units as u

class RcPanelSolver():

    import fas_pure as fas

    def __init__(self):
        print "RcRecSecSolver"
        
    def reinforce(self, panel, load, progress=None):
        b = 1.0 
        ap = panel.ap.asUnit(u.m).asNumber()
        an = panel.an.asUnit(u.m).asNumber()
        fip = panel.fip.asUnit(u.m).asNumber()
        fin = panel.fin.asUnit(u.m).asNumber()
        rysAp = panel.rysAp
        rysAn = panel.rysAn
        wlimp = panel.wlimp.asUnit(u.m).asNumber()
        wlimn = panel.wlimn.asUnit(u.m).asNumber()
        fcd = panel.fcd.asUnit(u.Pa).asNumber()
        fctm = panel.fctm.asUnit(u.Pa).asNumber()
        fyd = panel.fyd.asUnit(u.Pa).asNumber()
        #----
        pointnumber = len(panel.coord_Xp)
        panel.Apx = np.zeros(pointnumber)
        panel.Apy = np.zeros(pointnumber)
        panel.Anx = np.zeros(pointnumber)
        panel.Any = np.zeros(pointnumber)
        panel.rysx = np.zeros(pointnumber)
        panel.rysy = np.zeros(pointnumber)
        panel.mimosx = np.zeros(pointnumber)
        panel.mimosy = np.zeros(pointnumber)
        panel.ksieffx = np.zeros(pointnumber)
        panel.ksieffy = np.zeros(pointnumber)
        #----
        local_NX = load.force_equ_NX * (load.force_unit/u.N).asNumber()
        local_MX = load.moment_equ_MX * (load.moment_unit/u.Nm).asNumber()
        local_NY = load.force_equ_NY * (load.force_unit/u.N).asNumber()
        local_MY = load.moment_equ_MY * (load.moment_unit/u.Nm).asNumber()
        local_h = panel.h * (panel.h_unit/u.m).asNumber()
        #----
        for i in range(0, pointnumber):
            #----x direction
            tmp=self.fas.calc(local_NX[i], local_MX[i], local_h[i], b, ap, an, fip, fin, rysAp, rysAn, wlimp, wlimn, fcd, fctm, fyd)
            panel.Apx[i] = tmp['Ap']
            panel.Anx[i] = tmp['An']
            panel.rysx[i] = tmp['rys']
            panel.mimosx[i] = tmp['mimos']
            panel.ksieffx[i] = tmp['ksieff']
            #----y direction
            tmp=self.fas.calc(local_NY[i], local_MY[i], local_h[i], b, ap, an, fip, fin, rysAp, rysAn, wlimp, wlimn, fcd, fctm, fyd)
            panel.Apy[i] = tmp['Ap']
            panel.Any[i] = tmp['An']
            panel.rysy[i] = tmp['rys']
            panel.mimosy[i] = tmp['mimos']
            panel.ksieffy[i] = tmp['ksieff']
            if progress:
                progress.setValue(100 * i / pointnumber)
        #----unit definition
        panel.Apx = panel.Apx * (u.m / panel.A_unit).asNumber()
        panel.Anx = panel.Anx * (u.m / panel.A_unit).asNumber()
        panel.Apy = panel.Apy * (u.m / panel.A_unit).asNumber()
        panel.Any = panel.Any * (u.m / panel.A_unit).asNumber()
        #----
        if progress:
            progress.setValue(0)
        return None
# Test if main
if __name__ == '__main__':
    print ('test RcPanelSolver')
