# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *
from raasaft.alkane import *
from raasaft.aromatic import *
from raasaft.acid import *
from raasaft.alcohol import *

class Span80(MieCGHet):
    def __init__(self,count):
        # Initialize the different bead types
        self.C3 = MnMAlkane(C=3,count=1)
        self.PDA = PentadecanoicAcid(count=1)
        self.PTO = Pentatriol(count=1)
        self.OXL = Oxolane(count=1)
        # Put these in a list
        self.Components=[self.PDA, self.C3, self.PTO, self.OXL]
        # Give this compound a name and a short name
        self.Name = "Span80"
        self.ShortName = "S80"
        # Set the number of segments
        self.Segments = 12
        # This sets the particle numbering:
        self.Def = [self.OXL] + [self.PTO]*4 + [self.PDA]*6 + [self.C3]
        # Initialize the base class instance
        MieCGHet.__init__(self,count)
        #
        # Bond type 1 (APCbt1) is OXL-PTO, type 2 is PTO-PTO,
        # type 3 is PTO-PDA, type 4 is PDA-PDA, type 5 is PDA-C3
        self.NrBondTypes = 5
        bt1, bt2, bt3, bt4, bt5 = self.getBondNames()
        # Now configure the bonds
        self.Bonds =[( 0, 1,bt1), ( 0, 2,bt1), ( 1, 2,bt2), 
                    ( 2, 3,bt2), ( 3, 4,bt2), ( 4, 5,bt3), 
                    ( 5, 6,bt4), ( 6, 7,bt4), ( 7, 8,bt4), 
                    ( 8, 9,bt4), ( 9,10,bt4), (10,11,bt5)]
        # Make a list of the bond types, coefficients and lengths
        # Here, the first two bond types are rigid, and then three are flexible
        self.createBondSpec([2*6309.47]*2 + [SadiasBondConstant]*3)

        # Then define the angles.
        self.NrAngleTypes = 4
        at1, at2, at3, at4 = self.getAngleNames()
        self.Angles =[ (0,1,2,at1), (2,3,4,at2),
                       (3,4,5,at3), (4,5,6,at3), 
                       (5,6,7,at3), (6,7,8,at3),
                       (7,8,9,at4),
                       (8,9,10,at3), (9,10,11,at3) ]

        # Create the AngleSpec and AngleList. Pass in a list of tuples
        # containing (angle constant, equilibrium angle). 
        # First is a rigid OXL-PTO-PTO angle
        # Second is a rigid PTO-PTO-PTO angle
        # Third is flexible angles for the tail
        # Fourth is 120 deg cis angle to make the tail bend
        self.createAngleDataStructure([ 
                (3e5,61.57*math.pi/180.0), 
                (3e5,90.00*math.pi/180.0), 
                (SadiasAngleConstant,SadiasAngleZero),
                (3e5,120.00*math.pi/180.0)])
        #
        self.Citation = "DOI: unpublished"
        self.NagCite()
