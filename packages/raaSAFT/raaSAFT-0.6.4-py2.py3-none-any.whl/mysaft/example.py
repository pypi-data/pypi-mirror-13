# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class Example(MieCG): 
    def __init__(self,count=1):
        self.Name = "Example"
        self.Epsilon = 300*kBby10 
        self.Sigma = 4.0
        self.N = 12
        self.M = 6
        self.Segments = 1
        self.Mass = 35.0/self.Segments
        self.Citation = "DOI: Example"
        MieCG.__init__(self,count)
 
