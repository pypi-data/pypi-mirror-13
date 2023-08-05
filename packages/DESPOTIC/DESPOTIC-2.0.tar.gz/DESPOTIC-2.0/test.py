from despotic import cloud,zonedcloud
from despotic.chemistry import NL99,NL99_GC
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy import constants as constants
#import ipdb
import matplotlib

########################################################################
# User-settable options
########################################################################

column_density = 1.e22
NZONES = 8
########################################################################
# Program code
########################################################################



zc = zonedcloud(colDen = np.linspace(column_density/NZONES,
                                     column_density,NZONES))

zc.addEmitter('c+',1.e-100)
zc.addEmitter('c',2.e-4)
zc.addEmitter('o', 4.e-4)
zc.addEmitter('co',1.e-100)
        
zc.nH = 1.e3
zc.Td = 30
zc.rad.TradDust = 30
zc.Tg = 30
zc.ionRate = 3.e-17
zc.rad.ionRate = 3.e-17
zc.chi = 1.
zc.rad.chi = 1.

for nz in range(NZONES):
    zc.comp[nz].xH2 = 0.5
    zc.comp[nz].xHe = 0.1
    zc.emitters[nz]['co'].extrap = True
    zc.emitters[nz]['c+'].extrap = True
    zc.emitters[nz]['o'].extrap = True
    zc.emitters[nz]['c'].extrap = True
    zc.comp[nz].computeDerived(zc.zones[nz].nH)

sc = cloud()
sc.colDen = column_density

sc.addEmitter('c+',1.e-100)
sc.addEmitter('c',2.e-4)
sc.addEmitter('o', 4.e-4)
sc.addEmitter('co',1.e-100)

sc.nH = 1.e3
sc.Td = 30
sc.rad.TradDust = 30
sc.Tg = 30
sc.ionRate = 3.e-17
sc.rad.ionRate = 3.e-17
sc.chi = 1.
sc.rad.chi = 1.

sc.comp.xH2 = 0.5
sc.comp.xHe = 0.1
sc.emitters['co'].extrap = True
sc.emitters['c+'].extrap = True
sc.emitters['o'].extrap = True
sc.emitters['c'].extrap = True
sc.comp.computeDerived(sc.nH)

#import pdb; pdb.set_trace()

# Calculate chemical abundance

zc.setChemEq(network=NL99_GC, verbose=True)
sc.setChemEq(network=NL99_GC, verbose=True)

#H2.zones[0].setChemEq(network=NL99_GO,evolveTemp = 'iterateDust', verbose=True)
