# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class DimethylSulfide(MieCG): 
    def __init__(self,count):
        self.Epsilon=301.76*kBby10
        self.Sigma=3.661
        self.N=13.21
        self.M=6
        self.Name = "DMS"
        self.Segments = 2
        self.Mass = 62.13/self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: Unpublished"
        MieCG.__init__(self,count)
