# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages
from math import pi

# units: we adopt the following fundamental units courtesy of Vasileios Raptis
#       [distance] = 1 Angstroem = 10^-10 m
#       [energy]   = 10 J/mol    
#       [mass]     = 1 g/mol     = 10^-3 kg/mol
# 
# Then, time unit is
#       [time]   = ([mass] * [distance]^2 / [energy])^0.5 = 10^-12 s = 1 ps
# 
# In HOOMD-blue, temperature is given and reported as kB * T, in units of energy 
#       kB = 8.3144622 (J/mol)/K = 0.83144622 [energy]/K
# so, a temperature of, say, T = 300 K should be given as: 
#       0.83144622 X 300 = 249.433866 [energy]

# The above means we need a conversion factor for the energy:
kBby10=0.83144622
ConvToBar=166.053867
ConvFromBar=1.0/ConvToBar

# This is for converting kcal to J
kcal2joule=4184

# The following are from the SAFT-gamma Mie V paper where they use kcal/mol
# and angstrom. Angstrom is fine, but our energy unit is 10 J/mol. This
# is further complicated by the fact that they have a different 
# definition of the constant, so we must multiply by a factor 2.
SadiasBondConstant = 2*7.540*kcal2joule*0.1
RigidBondConstant = 2*17000
SadiasAngleZero = 157.6*pi/180.0
SadiasAngleConstant = 2*2.650*kcal2joule*0.1
