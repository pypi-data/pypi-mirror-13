# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class PentadecanoicAcid(MieCG): 
    
    def __init__(self,count=1):
        self.Name = "PDA"
        self.Epsilon = 467.05*kBby10 
        self.Sigma = 4.09
        self.N = 25.82
        self.M = 6
        self.Segments = 6
        self.Mass = 242.398/self.Segments
        self.Citation = "DOI: MnM"
        MieCG.__init__(self,count)
 
