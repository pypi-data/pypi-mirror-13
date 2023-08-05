# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *
from raasaft.alkanes import *
from raasaft.aromatic import *
from raasaft.sulfuric import *

class APCnew(MieCGHet):
    def __init__(self,count):
        # Initialize the different bead types
        self.C12 = MnMAlkane(C=12,count=1)
        self.ANT = Anthracene(count=1)
        self.PY  = Pyridine(count=1)
        # Put these in a list
        self.Components=[self.C12, self.ANT, self.PY]
        # Give this compound a name and a short name
        self.Name = "AsphalteneContinental"
        self.ShortName = "APC"
        # Set the number of segments
        self.Segments = 23
        # This sets the particle numbering: (0,1,2,3) are alkanes, (4,5,6) are
        # anthracenes, etc.
        self.Def = [self.C12]*4 + [self.ANT]*3 + [self.PY] + [self.ANT]*3 + [self.PY] + [self.ANT]*3 + [self.C12]*8
        # Initialize the base class instance
        MieCGHet.__init__(self,count)
        #
        # Bond type 1 (APCbt1) is alkane-alkane, type 2 is alkane-anthracene,
        # type 3 is anthracene-anthracene, type 4 is anthracene-pyridine.
        self.NrBondTypes = 4
        bt1, bt2, bt3, bt4 = self.getBondNames()
        # Now configure the bonds
        # These were imported from Carmelo's excel sheet on 29. Jan
        # Note that HOOMD has 0-based indexing while Gromacs has 1-based.
        self.Bonds =[( 0, 1,bt1), ( 1, 2,bt1), ( 2, 3,bt1), 
                    ( 3, 6,bt2), ( 4, 5,bt3), ( 4, 8,bt3), 
                    ( 4, 9,bt3), ( 5, 6,bt3), ( 5, 9,bt3), 
                    ( 5,10,bt3), ( 6, 7,bt4), ( 6,10,bt3), 
                    ( 8, 9,bt3), ( 8,12,bt3), ( 8,13,bt3), 
                    ( 9,10,bt3), ( 9,13,bt3), ( 9,14,bt3), 
                    (10,14,bt3), (11,12,bt4), (12,13,bt3), 
                    (12,15,bt2), (13,14,bt3), (14,19,bt2), 
                    (15,16,bt1), (16,17,bt1), (17,18,bt1), 
                    (19,20,bt1), (20,21,bt1), (21,22,bt1)]
        # Make a list of the bond types, coefficients and lengths
        self.createBondSpec([2*6309.47]*4)
        
        # Then set up the angles
        self.NrAngleTypes = 2
        at1, at2 = self.getAngleNames()
        # Specify which angles are which types
        self.Angles =[ ( 0,  1,  2, at1), ( 1,  2,  3, at1), 
                       ( 3,  6, 10, at2), ( 4,  5,  6, at2), ( 4,  8, 12, at2),
                       ( 5,  6,  7, at2), ( 5,  9, 13, at2), ( 6, 10, 14, at2),
                       ( 8,  9, 10, at2), (11, 12, 13, at2), (12, 13, 14, at2),
                       (10,  6,  3, at2), ( 8, 12, 15, at2), (13, 14, 19, at2),
                       (15, 16, 17, at1), (16, 17, 18, at1), 
                       (19, 20, 21, at1), (20, 21, 22, at1) ]
        # Then create the data structure. Pass in a list of tuples containing
        # the angle constant and equilibrium angle for each type of angles.
        self.createAngleDataStructure([(SadiasAngleConstant,SadiasAngleZero),(3e5,180.00*math.pi/180.0)])
        #
        self.Citation = "DOI: unpublished"

class ResinB(MieCGHet):
    def __init__(self,count):
        # Initialize the different bead types
        self.C2 = MnMAlkane(C=2,count=1)
        self.C3 = MnMAlkane(C=3,count=1)
        self.DMS = DimethylSulfide(count=1)
        self.CYH = Cyclohexane(count=1)
        self.BEN = Benzene2(count=1)
        self.PYR = Pyrrole(count=1)
        # Put these in a list
        self.Components=[self.C2, self.C3, self.DMS, self.CYH, self.BEN, self.PYR]
        # Give this compound a name and a short name
        self.Name = "ResinB"
        self.ShortName = "RES"
        # Set the number of segments
        self.Segments = 12
        # This sets the particle numbering.
        self.Def = [self.C3] + [self.DMS]*2 + [self.C2] + [self.CYH] + [self.BEN]*2\
                 + [self.PYR] + [self.C2] + [self.DMS]*2 + [self.C3]
        # Initialize the base class instance
        MieCGHet.__init__(self,count)
        #
        # Set up the bonds. We have 8 types of bonds here.
        self.NrBondTypes = 8
        # Make some names for these bonds
        bt1, bt2, bt3, bt4, bt5, bt6, bt7, bt8 = self.getBondNames()
        # Now define these bonds, i.e. between bead 0 and 1 we have type 1, etc.
        # Bond type 1 is C3-DMS, type 2 is DMS-DMS, type 3 is DMS-C2,
        # type 4 is C2-CYH, type 5 is CYH-BEN, type 6 is BEN-BEN, type 7 is
        # BEN-PYR, type 8 is PYR-C2.
        self.Bonds =[ (0,1,bt1), (1,2,bt2), (2,3,bt3), 
                      (3,4,bt4), (4,5,bt5), (5,6,bt6), 
                      (6,7,bt7), (7,8,bt8), (8,9,bt3), 
                      (9,10,bt2), (10,11,bt1) ]
        # Create the full bond specification. Pass in a list of the bond
        # constants. Here, all of them are Sadia's. The bond lengths are
        # calculated from self.Bond such that the beads are tangentially bonded.
        self.createBondSpec([SadiasBondConstant]*8)

        # Then define the angles.
        self.NrAngleTypes = 2
        at1, at2 = self.getAngleNames()
        self.Angles =[ (0,1,2,at1), (1,2,3,at1), (2,3,4,at1),
                       (3,4,5,at2), (4,5,6,at2), (5,6,7,at2), (6,7,8,at2),
                       (7,8,9,at1), (8,9,10,at1), (9,10,11,at1) ]
        # Create the AngleSpec and AngleList. Pass in a list of tuples
        # containing (angle constant, equilibrium angle). Here, the first is
        # a flexible alkane-type angle and the second is a rigid 120 deg angle.
        self.createAngleDataStructure([(SadiasAngleConstant,SadiasAngleZero),(3e5,120.00*math.pi/180.0)]) 
        #
        self.Citation = "DOI: unpublished"


