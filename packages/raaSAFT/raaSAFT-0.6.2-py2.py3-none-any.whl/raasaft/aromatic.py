# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages
from math import pi
# Other parts of raasSAFT
from raasaft.mie import *
from raasaft.constants import *

class Toluene(MieCG):
    def __init__(self,count):
        self.Name = "Toluene"
        self.Epsilon=411.870*kBby10
        self.Sigma=4.266
        self.N=16.9532
        self.M=6
        self.Segments = 2
        self.Mass = 92.14 / self.Segments 
        self.BondConstant = RigidBondConstant
        self.BondLength = self.Sigma
        self.Citation = "DOI: 10.1021/ie404247e"
        MieCG.__init__(self,count)

class Benzene1(MieCG):
    def __init__(self,count):
        self.Name = "Benzene"
        self.Epsilon=658.17*kBby10
        self.Sigma=5.293
        self.N=32
        self.M=6
        self.Segments = 1
        self.Mass = 78.11 / self.Segments
        self.Citation = "DOI: 10.1080/00268976.2012.662303"
        MieCG.__init__(self,count)

class Benzene2(MieCG): 
    def __init__(self,count):
        self.Name = "Benzene"
        self.Epsilon=353.93*kBby10
        self.Sigma=3.978
        self.N=14.23
        self.M=6
        self.Segments = 2
        self.Mass = 78.11 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: M&M?"
        MieCG.__init__(self,count)

class Benzene3(MieCG):
    def __init__(self,count):
        self.Name = "Benzene"
        self.Epsilon=258.28*kBby10
        self.Sigma=3.490
        self.N=11.58
        self.M=6
        self.Segments = 3
        self.Mass = 78.11 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Bonds = [(0,1), (1,2), (2,0)]
        self.Citation = "DOI: 10.1080/00268976.2012.662303"
        MieCG.__init__(self,count)

class Pyridine(MieCG):
    def __init__(self,count):
        self.Name = "Pyridine"
        self.Epsilon=410.46*kBby10
        self.Sigma=3.90
        self.N=15.52
        self.M=6
        self.Segments = 2
        self.Mass = 79.10 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: M&M"
        MieCG.__init__(self,count)

class Anthracene(MieCG):
    def __init__(self,count):
        self.Name = "Anthracene"
        self.Epsilon=409.80*kBby10
        self.Sigma=3.560
        self.N=14.789
        self.M=6
        self.Segments = 5
        self.Mass = 178.23 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Bonds = [(0,1), (1,2), (0,3), (1,3), (1,4), (2,4), (3,4)]
        self.NrAngleTypes = 2
        at1, at2 = self.getAngleNames()
        self.Angles = [(0,1,2,at1), (0,3,4,at2), (2,4,3,at2)]
        self.AngleSpec = [ [at1,3e5,pi], [at2,3e5,120*pi/180] ]
        self.Citation = "DOI: M&M?"
        MieCG.__init__(self,count)

class Oxolane(MieCG):
    def __init__(self,count):
        self.Name = "Oxolane"
        self.Epsilon=348.92*kBby10
        self.Sigma=3.840
        self.N=14.8455
        self.M=6
        self.Segments = 2
        self.Mass = 72.11 / self.Segments
        self.Citation = "DOI: M&M"
        MieCG.__init__(self,count)

class Cyclohexane(MieCG):
    def __init__(self,count):
        self.Name = "Cyclohexane"
        self.Epsilon=345.94*kBby10
        self.Sigma=4.234
        self.N=14.05
        self.M=6
        self.Segments = 2
        self.Mass = 84.16 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: M&M"
        MieCG.__init__(self,count)

class Pyrrole(MieCG):
    def __init__(self,count):
        self.Name = "Pyrrole"
        self.Epsilon=512.575*kBby10
        self.Sigma=3.771
        self.N=23.302
        self.M=6
        self.Segments = 2
        self.Mass = 67.09 / self.Segments
        self.BondConstant = RigidBondConstant
        self.Citation = "DOI: M&M"
        MieCG.__init__(self,count)
