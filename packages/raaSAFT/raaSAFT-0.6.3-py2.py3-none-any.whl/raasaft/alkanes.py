# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages
import math
# Other parts of raasaft
from raasaft.mie import *
from raasaft.constants import *

# This is the alkane class based on the M&M correlation.
class MnMAlkane(MieCG):
	
    # Define tables that give the sigma, epsilon, repulsive exponent and number of beads for 
    # different alkanes. Python arrays are zero-indexed, so the first entry 
    # corresponds to C0, which is nonsensical and should never be used.
    # The epsilons here are given as (epsilon/k_B) in Kelvin. The energy 
    # unit we want to use is 10 J/mol, so we need to convert it. Sigma is in 
    # angstrom, which is OK. So multiply epsilon by k_B (in J/mol) divided by 10
    #                   C0   C1     C2     C3     C4     C5     C6     C7     C8     C9     C10    C11    C12  C13  C14  C15  C16  C17  C18  C19  C20
    SigmaTable  =       [0, 3.752, 4.349, 4.871, 3.961, 4.248, 4.508, 4.766, 4.227, 4.406, 4.584, 4.216, 4.351, 0, 4.183, 0, 4.432, 0, 4.262, 0, 4.487]
    EpsilonTableK =     [0, 170.8, 330.3, 426.1, 256.4, 317.5, 376.4, 436.1, 333.7, 374.2, 415.2, 348.9, 378.6, 0, 363.1, 0, 418.1, 0, 393.7, 0, 453.1]
    EpsilonTable =      [ e*kBby10 for e in EpsilonTableK ]
    RepulsiveExpTable = [0, 16.39, 27.30, 34.29, 13.29, 16.06, 19.57, 23.81, 16.14, 18.31, 20.92, 16.84, 18.41, 0, 17.66, 0, 21.20, 0, 19.53, 0, 24.70]
    SegmentTable =      [0,   1,     1,     1,     2,     2,     2,     2,     3,     3,     3,     4,     4,   0,   5,   0,   5,   0,   6,   0,   6  ]

    # This is the function called when you do e.g. C10=MnMAlkane(10)
    def __init__(self,C,count):

        if self.SigmaTable[C] == 0:
            print("ERROR: Specified alkane carbon number", self.minCarbonNumber)
            error("has not been implemented with the MnM model!")

        self.Name = "C{0}".format(C)
        self.Epsilon=self.EpsilonTable[C]
        self.Sigma=self.SigmaTable[C]
        self.N=self.RepulsiveExpTable[C]
        self.M=6
        self.Segments = int(self.SegmentTable[C])
        self.Mass = (15.035 + (C-1)*14.027 + 1.008)/self.Segments
        self.BondConstant = SadiasBondConstant
        self.BondLength = self.Sigma
        self.AngleZero = SadiasAngleZero
        self.AngleConstant = SadiasAngleConstant
        self.FirstSeg = 0
        self.LastSeg = self.Segments-1
        self.Citation = "DOI: 10.1021/ie404247e"
        MieCG.__init__(self,count)

# This is the homonuclear CG alkane model of Olga. It works for arbitrary
# alkanes, but the accuracy is a little bit lower when the carbon number is not
# evenly divisible by three.
class HomoAlkane(MieCG):
	
    # Define tables that give the sigma, epsilon for different alkanes
    # Python arrays are zero-indexed, so the first entry corresponds to C0,
    # which is nonsensical and should never be used in simulations.
    # The epsilons here are given as (epsilon/k_B) in Kelvin. The energy 
    # unit we want to use is 10 J/mol, so we need to convert it. Sigma is in 
    # angstrom, which is OK. So multiply epsilon by k_B (in J/mol) divided by 10
    #               C0 C1 C2 C3 C4     C5      C6      C7      C8      C9     C10     C11     C12     C13     C14     C15
    SigmaTable   =  [0, 0, 0, 0, 0, 4.2449, 4.5089, 4.5736, 4.2412, 4.4212, 4.4908, 4.2212, 4.3635, 4.4680, 4.2332, 4.3286]
    EpsilonTableK = [0, 0, 0, 0, 0, 310.78, 342.00, 380.87, 321.65, 344.83, 363.99, 328.18, 344.42, 354.25, 329.81, 344.85]
    EpsilonTable =  [ e*kBby10 for e in EpsilonTableK ]
	 

    # This is the function called when you do e.g. C10=HomoAlkane(10)
    def __init__(self,C,count):

        if self.SigmaTable[C] == 0:
            print("ERROR: Specified carbon number: ", self.minCarbonNumber)
            error("has not been implemented for the homonuclear model!")

        self.Name = "C{0}".format(C)
        self.Epsilon=self.EpsilonTable[C]
        self.Sigma=self.SigmaTable[C]
        self.N=15
        self.M=6
        # This sets the number of segments based on the carbon number C
        self.Segments = math.ceil((C-1)/3)
        # This sets the mass per bead based on the number C: CH3 + (C-1)*CH2 + H
        self.Mass = (15.035 + (C-1)*14.027 + 1.008)/self.Segments
        self.BondConstant = SadiasBondConstant
        self.BondLength = self.Sigma
        self.AngleZero = SadiasAngleZero
        self.AngleConstant = SadiasAngleConstant
        self.FirstSeg = 0
        self.LastSeg = self.Segments-1
        self.Citation = "DOI: Unpublished"
        MieCG.__init__(self,count)


