# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages
from math import floor
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class BioWater(MieCG): 
    def __init__(self,count):
        # Remark: this has two water molecules per bead, so we construct count/2
        # beads.
        self.Name = "H2O"
        self.Epsilon=400.0*kBby10
        self.Sigma=3.7467
        self.N=8
        self.M=6
        self.Segments = 1
        self.RMax = 20 # Angstrom, from the paper, overrides default
        self.Citation = "DOI: 10.1080/00268976.2015.1004804"
        MieCG.__init__(self,floor(count/2))
