# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from builtins import *
# Other packages we need
from itertools import combinations, islice
from raasaft.main import setCrossPotCoeff, addAngle, getGroup, Mie

# Class containing things that are common to both homonuclear and heteronuclear
class MieCGbase:
    
    def __init__(self):
        pass

    # This returns a dict that is used in create_random_polymers
    def getPolyDict(self,bond_len=3.5):
        # Use the bond from the constructor
        return dict(bond_len=bond_len, type=self.Types,bond=self.Bonds, count=self.Count)
    
    # Convenience function for setting the bond coefficients
    def setBondCoeff(self,bondList):
        try:
            for spec in self.BondSpec:
                name, b, r = spec
                bondList.bond_coeff.set(type=name,k=b,r0=r)    
        except AttributeError:
            error("Cannot set bond coefficent on"+self.Name)
    
    # Convenience function for setting the angle potential coefficients
    def setAngleCoeff(self,angleList):
        for spec in self.AngleSpec:
            name, k, t0 = spec
            angleList.set_coeff(name,k,t0)
    

    def createAngles(self,system):
        # Only add angles if three beads or more
        if self.Segments > 2:
            # First, add the angles.
            try:
                # Works for heteronuclear
                for a in self.AngleList:
                    addAngle(system,name=a)
            except AttributeError:
                # component didn't have AngleList, try AngleName (homonuclear)
                addAngle(system,name=self.AngleName)
            # Create this group of particles
            self.Group = getGroup(self)
            # Create an iterator that iterates through the molecules belonging to
            # this group.
            iterMolec = islice(iter(self.Group),0,None,self.Segments)
            # Go through the molecules and add all angles
            for p in iterMolec:
                i = p.tag
                for angle in self.Angles:
                    # From this angle, make a proper spec that goes into system.angles.add()
                    # First get the offset into the particle list. This is the
                    # number of the current molecule, plus the number of the current
                    # bead inside that molecule.
                    # Then create the spec. We have to flip so that the name goes
                    # first, since HOOMD expects this.
                    spec = [ angle[3], angle[0] + i, angle[1] + i, angle[2] + i ]
                    # Then add this angle to the system. We must splat the list.
                    system.angles.add(*spec)

    # Function that returns canonical bond names for a component
    def getBondNames(self):
        names = []
        for n in range(1,self.NrBondTypes+1):
            self.ShortName = getattr(self,"ShortName",self.Name[0:3]) 
            names.append(self.ShortName+"bt{0}".format(n))
        return names

    # Function that returns canonical angle names for a component
    def getAngleNames(self):
        names = []
        for n in range(1,self.NrAngleTypes+1):
            self.ShortName = getattr(self,"ShortName",self.Name[0:3]) 
            names.append(self.ShortName+"at{0}".format(n))
        return names
    
    # In case someone tries to print() a molecule
    def __str__(self):
        return u"%s molecules of %s, using %s" % (self.Count, self.Name, self.Citation)

# Homonuclear class
class MieCG(MieCGbase):

    def __init__(self,count):
        MieCGbase.__init__(self)
        self.Count = int(count)
        self.RMin = 0.3*self.Sigma
        self.RMax = 6.0*self.Sigma
        self.Separation = 0.7
        # Don't remove the trailing comma here     \/ (compatibility with heteronuclear)
        self.NameSep = (self.Name, self.Separation),
        self.Coeff = dict(epsilon=self.Epsilon,
                          sigma=self.Sigma,
                          n=self.N,
                          m=self.M)
        self.kij = dict() # Empty dict for holding kij's from user input
        self.BondLength = self.Sigma # Default, tangential bonding
        self.Types = [self.Name] * self.Segments
        self.ShortName = self.Name[0:3]
        self.BondName = self.ShortName+"bt1"
        self.NrBondTypes = 1
        # Set the bond layout
        if self.Segments == 1:
            self.Bonds = "linear"
        else:
            # First specify the default (linear layout)
            bond = [ (i,i+1) for i in range(self.Segments-1) ]
            # If the compound specifies a custom bond layout, use that, else use the linear default
            bond = getattr(self,"Bonds",bond)
            # Go through and tack on the bond name
            bond = [ (b[0],b[1],self.BondName) for b in bond ]
            # Set it
            self.Bonds = bond
            # Make the BondSpec, for compatibility with heteronuclear
            self.BondSpec = [ [self.BondName, self.BondConstant, self.BondLength] ]
        # Set the angle spec if angle const and angle zero has been set, but not AngleSpec
        if not hasattr(self,"AngleSpec"):
            try:
                self.AngleName = self.ShortName+"at1"
                self.NrBondTypes = 1
                # Build the angle spec
                self.AngleSpec = [ [self.AngleName, self.AngleConstant, self.AngleZero] ]
                self.Angles = [ (n, n+1, n+2, self.AngleName) for n in range(self.Segments-2) ]
            except AttributeError:
                # This means user has not specified angle constant and zero.
                pass
        # If Angles has not yet been set, give empty list so we can still "loop" over it
        if not hasattr(self,"Angles"):
            self.Angles = []


    # The cutoff can be changed after instantiation
    def setCutoff(self,RMax):
        self.RMax = RMax


    # The cutoff can be changed after instantiation
    def setInCutoff(self,RMin):
        self.RMin = RMin
 

    # Convenience function for setting the potential coefficents
    def setPotCoeff(self,mie):
        if mie.isTable:
            mie.pair_coeff.set(self.Name, self.Name, func=Mie,
                             rmin=self.RMin, rmax=self.RMax,
                             coeff=dict(self.Coeff))
        else:
            mie.pair_coeff.set(self.Name, self.Name, r_cut=self.RMin, **self.Coeff)


# The base class for heteronuclear components
class MieCGHet(MieCGbase):
    
    def __init__(self,count):
        MieCGbase.__init__(self)
        # First a quick sanity check
        if len(self.Def) != self.Segments:
            error("Definition of "+self.Name+" inconsistent with # of segments!") 
        self.Count = int(count)
        # Give all the sub-components new names that are unique to this
        # heteronuclear component
        for comp in self.Components:
            comp.Name = comp.ShortName+self.ShortName
        # Set up the NameSep nested tuple for all the components
        self.NameSep = tuple( (c.Name,0.7) for c in self.Components)
        # Set up the Types array containing all the names the right number of times
        self.Types = [ d.Name for d in self.Def ]
        # Define the average sigma for the heteronuclear component
        self.Sigma = sum([ d.Sigma for d in self.Def ])/self.Segments


    # Convenience function for setting the potential coefficents
    def setPotCoeff(self,mie):
        # First set all coefficients for same components
        for comp in self.Components:
            if mie.isTable:
                mie.pair_coeff.set(comp.Name, comp.Name, func=Mie, 
                                   rmin=comp.RMin, rmax=comp.RMax, 
                                   coeff=dict(comp.Coeff))
            else:
                mie.pair_coeff.set(comp.Name, comp.Name, r_cut=comp.RMin, **comp.Coeff)
        # Then set all the cross interactions (python coolness)
        for (A,B) in combinations(self.Components,2):
            setCrossPotCoeff(mie,A,B)
 
    def createAngleDataStructure(self,angleConstEquil):
        # Get the angle names
        self.AngleList = self.getAngleNames()
        # zip is it's own inverse (an involution). We also need to splat the
        # argument. So this gives us two lists, one containing angle constants, 
        # the other containing equilibrium angles.
        ks, t0s = zip(*angleConstEquil)
        # Then create the list of lists that is the AngleSpec
        self.AngleSpec = [ [name, ks[i], t0s[i]] for i, name in enumerate(self.AngleList) ]

    def createBondSpec(self,bondConstants):
        # get the bond names
        self.bondList = self.getBondNames() 
        # loop through Bonds and calculate the bond lenghts, put in a list
        bondLengths = []
        # Loop through the bond types
        for bondNr in range(1,self.NrBondTypes+1):
            # Find two beads that have this bond
            # Look through all the different bonds
            for candidate in self.Bonds:
                # If this bond has the correct name
                if candidate[2] == self.ShortName+"bt"+str(bondNr):
                    # Get the bead numbers corresponding to this bond
                    bead1, bead2 = candidate[0:2]
                    # Exit the "candidate" loop, since we found what we're looking for
                    break
            # Add up the size of these two beads, divide by two, and add it to the list
            bondLengths.append(0.5*(self.Def[bead1].Sigma + self.Def[bead2].Sigma))
        # finally set up the BondSpec list of lists
        self.BondSpec = [ [ name, bondConstants[i], bondLengths[i] ] for i, name in enumerate(self.bondList)]

