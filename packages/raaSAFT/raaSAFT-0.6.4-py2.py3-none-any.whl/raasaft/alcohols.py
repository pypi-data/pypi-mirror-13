# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class Pentatriol(MieCG):
    def __init__(self,count):
        self.Name = "PTO"
        self.Epsilon=535.35*kBby10
        self.Sigma=3.49
        self.N=22.04
        self.M=6
        self.Segments = 4
        self.Mass = 120.147/self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: Unpublished"
        MieCG.__init__(self,count)
