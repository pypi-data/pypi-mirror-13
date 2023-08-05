# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class CO2(MieCG): 
    def __init__(self,count):
        self.Name = "CO2"
        self.Epsilon=353.55*kBby10
        self.Sigma=3.741
        self.N=23
        self.M=6.66
        self.Segments = 1
        self.Mass = 44.01 / self.Segments
        self.Citation = "DOI: 10.1021/jp204908d"
        MieCG.__init__(self,count) 

class N2(MieCG): 
    def __init__(self,count):
        self.Name = "N2"
        self.Epsilon=122.85*kBby10
        self.Sigma=3.653
        self.N=20.02
        self.M=6
        self.Segments = 1
        self.Mass = 28.01 / self.Segments
        self.Citation = "DOI: 10.1021/jp204908d"
        MieCG.__init__(self,count)
