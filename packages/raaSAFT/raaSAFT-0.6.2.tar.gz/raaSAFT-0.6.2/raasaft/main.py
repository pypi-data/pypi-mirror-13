# For Python2 support:
from __future__ import (absolute_import, division,print_function)
from future.standard_library import install_aliases
install_aliases()
from builtins import *
# Other packages we need
from hoomd_script import *
import sys
import re
from math import sqrt, pi
from itertools import combinations, islice, product, combinations_with_replacement
from random import uniform
import xml.etree.ElementTree as et
import requests
from datetime import datetime
from shutil import copyfile

# Monkey patch context.initialize such that it will exist but do nothing on
# older HOOMD-blue versions
try:
    dir(context)
except NameError:
    class context:
        def initialize():
            pass

# Global list for holding citations
compdoi = []
# Function for building this list
def compdoiBuild(components):
    # Set the general method reference as the first
    compdoi.append(("General method","10.1146/annurev-chembioeng-061312-103314"))
    compdoi.append(("Combining rules","10.1080/00268976.2012.662303"))
    # Extract valid DOIs in the system. Valid DOIs start with 10.X where X is a number with at least 3 digits.
    for comp in components:
        trydoi = re.search("10.[0-9]{3,}\S+", comp.Citation)
        if trydoi != None and not any(comp.Name == a for (a,b) in compdoi):
            compdoi.append((comp.Name,trydoi.group(0)))


# Debugging toggle. Defaults to false.
debug = False
def EnableDebugging():
    debug = True
def IsDebug():
    return debug

# Error function for printing error message and quitting.
def error(message):
    if comm.get_rank() == 0: 
        sys.stderr.write("ERROR: %s\n" % message)
    sys.exit(1)

# Analytical Mie potential and force
def Mie(r, rmin, rmax, epsilon, sigma, n, m):
    prefactor = (n/(n-m))*(n/m)**(m/(n-m))*epsilon
    V = prefactor*(  (sigma/r)**n -   (sigma/r)**m)
    F = prefactor*(n*(sigma/r)**n - m*(sigma/r)**m)/r
    return (V, F)

# Does what it says on the tin
def resizeBox(initialBox,factor,Nstart,Nstop,resizePeriod):
    iLx, iLy, iLz = [initialBox.Lx, initialBox.Ly, initialBox.Lz]
    shrink_Lx = variant.linear_interp(points = 
                [(Nstart, iLx),(Nstop, iLx*factor)]
                                     )
    shrink_Ly = variant.linear_interp(points = 
                [(Nstart, iLy),(Nstop, iLy*factor)]
                                     )
    shrink_Lz = variant.linear_interp(points = 
                [(Nstart, iLz),(Nstop, iLz*factor)]
                                     )
    return update.box_resize(Lx=shrink_Lx, Ly=shrink_Ly, Lz=shrink_Lz,period=resizePeriod)

def volumePreservingStretch(box,stretch):
    # Get the old box lengths
    iLx, iLy, iLz = [ box.Lx, box.Ly, box.Lz ]
    print("Old volume:"+str(iLx*iLy*iLz))
    # If stretch > 1.0 it means we make Lz longer and Lx, Ly shorter.
    newLx = iLx/sqrt(stretch)
    newLy = iLy/sqrt(stretch)
    newLz = iLz*stretch
    print("New volume:"+str(newLx*newLy*newLz))
    return update.box_resize(Lx=newLx,Ly=newLy,Lz=newLz,period=None)

def setCrossInteraction(A,B,kij):
    # Set this kij into the dict for both components, under the name of the other.
    try:
        A.kij[B.Name] = kij
        B.kij[A.Name] = kij
    except AttributeError:
        # Heteronuclear components have no kij dict, and setting kij on them makes no sense.
        error("Cannot set kij on a heteronuclear component. Do it on each subcomponent.")

# Set the cross interactions and the potential coefficients for this pair
def setCrossPotCoeff(mie,A,B,zeroIt=False):
    # The reference for this is Lafitte 
    SigmaAB = 0.5*(A.Sigma + B.Sigma)
    nAB = 3 + sqrt((A.N-3)*(B.N-3))
    mAB = 3 + sqrt((A.M-3)*(B.M-3))
    # Get the kij, default to zero if user has not set anything
    kAB = A.kij.get(B.Name,0.0)
    # The zeroIt Boolean is set if we are not "keeping" this interaction
    if zeroIt:
        EpsilonAB = 0.0
    else:
        EpsilonAB = (1.0-kAB)*(sqrt(A.Sigma*B.Sigma)/SigmaAB)**3*sqrt(A.Epsilon*B.Epsilon)
    ABCoeff = dict(epsilon=EpsilonAB,sigma=SigmaAB,n=nAB,m=mAB)
    if mie.isTable:
        mie.pair_coeff.set(A.Name, B.Name, func=Mie,
                             rmin=min(A.RMin,B.RMin), rmax=max(A.RMax,B.RMax),
                             coeff=dict(ABCoeff))
    else:
        mie.pair_coeff.set(A.Name, B.Name, rmax=max(A.RMax,B.RMax), **ABCoeff)

# Create the dict holding the separations
def getSepDict(components):
    # Python coolness. Google "python list comprehension".
    return dict([NameSep for comp in components for NameSep in comp.NameSep])

# Get the list of dicts specifying the polymers
def getPolyDicts(components):
    # All components have been specified now, so this is a good time to build 
    # the compdoi list.
    compdoiBuild(components)
    # Then nag about citing us
    if comm.get_rank() == 0: 
        citeNag(components)
    # Return the list of polymer dicts for HOOMD init
    return list(c.getPolyDict() for c in components)

# Decorator for the HOOMD cite.save() function
def addOurCites(save):
    def inner():
        dumpBibTeX()
        return save()
    return inner

# Decorate it, adding our citation dump
cite.save = addOurCites(cite.save)

# Nag about citing us
def citeNag(components):
    print("----")
    print("You are using raaSAFT, the SAFT-gamma Mie coarse grained simulation tools.")
    print(" ")
    print("Please also cite the following papers:")
    i = 0
    for name,doi in compdoi:
        i += 1
        if i < 3:
            print("* {0:50} {1}".format(name+":", doi))
        else:
            print("* Coarse grained {0:35} {1}".format(name+":", doi))
    print("Calling cite.save() will save the BibTeX for these to file.")
    print("-----")

# Takes a DOI and returns a BibTeX block
def doi2bib(doi): 
    url = "http://dx.doi.org/" + doi
    r = requests.get(url,headers={"accept":"application/x-bibtex"})
    r.encoding = "UTF-8"
    return r.text

# Loop over name,doi pairs, convert doi to BibTeX block, write all blocks to file
def dumpBibTeX():
        with open('raaSAFT-citations.bib', 'w') as bib:
            for name,doi in compdoi:
                bib.write(name+"\n"+doi2bib(doi)+"\n")


def setCutoff(theSystem, cutoff=0):
    # Hookd to silence some of the annoying HOOMD output if debug is off. It's
    # here since setupSimBox is usually the first function to be called.
    silenceInitOutput()
    # First extract any subcomponents of heteronuclear stuff
    components = getAllSubComponents(theSystem)
    if cutoff == 0:
        # This means the user wants automatic cutoff setup
        # Get the largest cutoff and use that
        # Python coolness: google "python max key lambda"
        cutoff = max(components, key=lambda c: c.RMax).RMax
    # Now we know the cutoff (either automatic or user specified), so set it
    for comp in components:
        comp.setCutoff(cutoff)

def addAngle(system,name):
    # We need a snapshot to modify the angles. Try/except bc. of API change.
    # We remove the default "angleA" if it exists, and then add the angle we
    # want.
    try:
        snap = system.take_snapshot(angles=True)
        if snap.angle_data.type_mapping.__contains__("angleA"):
            if snap.angle_data.type_mapping.__getitem__(0) == "angleA":
                snap.angle_data.type_mapping.__delitem__(0)
            else:
                error("Could not find the item id of angleA")
        snap.angle_data.type_mapping.append(name)
    except:
        snap = system.take_snapshot(bonds=True)
        snap.angles.types = [a for a in snap.angles.types if a != "angleA"] + [name]
    system.restore_snapshot(snap)

# Function for getting the group containing all particles belonging to a 
# (possibly heteronuclear) component
def getGroup(comp):
    # Try looping through subcomponents as if this was heteronuclear,
    # and set the group. If that failed, this is homonuclear, so we catch the
    # AttributeError and set the plain group based on the name.
    try:
        # Set g to a dummy string to handle the first subcomponent right
        g = "dummy"
        for comp in comp.Components:
            compGr = group.type(type=comp.Name)
            if g == "dummy":
                # This means compGr is the first subcomponent. Set g to it.
                g = compGr
            else:
                # Else do a union with compGr and what we have previously
                g = group.union(a=g,b=compGr,name=comp.Name+"-group")
    except AttributeError:
        g = group.type(type=comp.Name)
    return g

def setAllCrossCoeff(comps,table,keep="All"):
    # Assumes all kij = 0
    # First, get the subcomponents from any heteronuclear stuff
    components = getAllSubComponents(comps)
    # Set the list of cross-interactions to keep, defaults to all combinations
    # This feature is to enable logging of partial energies (e.g. only
    # solvent-polymer and not polymer-polymer or solvent-solvent energies)
    if keep == "All":
        keep = combinations(components,2)
    else:
        # expand any subcomponents in the keep list of tuples
        tokeep = []
        for k in keep:
            # Either k is a tuple, (A,B), or a single component, C.
            if isinstance(k,tuple):
                (A,B) = k
                tokeep.extend(product(subComps(A),subComps(B)))
            else:
                C = k
                tokeep.extend(combinations(subComps(C),2))
        keep = tokeep
    # Then we generate all unique combinations and set the cross interactions
    for (A,B) in combinations(components,2):
        if (A,B) in keep:
            setCrossPotCoeff(table,A,B)
        else:
            setCrossPotCoeff(table,A,B,zeroIt=True)

def getAllSubComponents(comps):
    # Unwrap the system to get any sub-components from heteronuclear components
    allComponents = []
    for comp in comps:
            allComponents.extend(subComps(comp))
    return allComponents
   
def subComps(comp):
    if len(comp.NameSep) == 1:
        return [comp]
    else:
        return comp.Components

def setPotentialCoeffs(components,mie,keep="All"):
    if keep == "All":
        keep = components
    for comp in components:
        if comp in keep:
            comp.setPotCoeff(mie)
        else:
            setDummyCoeff(comp,mie)

def setDummyCoeff(comp,mie):
        for scomp in subComps(comp):
            # Here we must use dict() to copy the dict before we modify it
            dummyCoeff = dict(scomp.Coeff)
            dummyCoeff['epsilon'] = 0.0
            if mie.isTable:
                mie.pair_coeff.set(scomp.Name, scomp.Name, func=Mie,
                                 rmin=scomp.RMin, rmax=scomp.RMax,
                                 coeff=dict(dummyCoeff))
            else:
                mie.pair_coeff.set(scomp.Name, scomp.Name, r_cut=scomp.RMin,**dummyCoeff)
        # Then zero all the cross interactions if this is heteronuclear
        try:
            for (A,B) in combinations(comp.Components,2):
                setCrossPotCoeff(mie,A,B,zeroIt=True)
        except AttributeError:
            # This means it's not heteronuclear, do nothing
            pass
    
def setupSimBox(components,elong=1.0,packing=0.1,dim=3):
    # Get total (number of beads * bead radius ^3) for all components
    NbeadRad3 = sum([ c.Count*c.Segments*c.Sigma**3 for c in components ])
    # Compute basic box side length
    bL = ( 4.0*pi*NbeadRad3/(elong*3.0*packing) )**(1.0/3.0)
    # Set box sides with optional elongation in z-direction
    bLx = bL/elong**(1/3)
    bLy = bL/elong**(1/3)
    bLz = bL*elong**(2/3)
    # Pass the sizes to HOOMD, which creates a box object that we return
    return data.boxdim(Lx=bLx, Ly=bLy, Lz=bLz, dimensions=dim)

def silenceInitOutput():
    if not debug:
        # Turn off notices for the init part
        option.set_notice_level(0)
        # Decorate and override the group.all() function from HOOMD so that we
        # can use it to turn output back on after init has finished.
        integrate.mode_standard = addUnsilence(integrate.mode_standard)

def addUnsilence(integrate):
    # This is a decorator
    def inner(dt):
        option.set_notice_level(2)
        return integrate(dt)
    return inner

def getEndToEndList(comp):
    # Returns a list of end-to-end distances of each molecule in this group.
    if comp.Segments == 1:
        return [0.0] * int(comp.Count) # One-bead component has zero end-to-end dist
    # First create two iterators that go through first and last segments, respectively
    iterFirstSeg = islice(iter(comp.Group),comp.FirstSeg,None,comp.Segments)
    iterLastSeg = islice(iter(comp.Group),comp.LastSeg,None,comp.Segments)
    # Zip these together to have an iterator that returns each pair of (first,last)
    iterEnds = zip(iterFirstSeg,iterLastSeg)
    # Go through each pair of (first,last) and calculate distance
    return [ sqrt(sum( (a-b)**2 for a,b in zip(p.position,q.position) )) for p,q in iterEnds ]

def addParticles(system,comp,count):
    # Only heteronuclear has sub-components
    newTags = []
    if hasattr(comp,'Components'):
        pass
        # handle the heteronuclear case TODO
    else:
        for c in range(count):
            tags = [0]*comp.Segments
            for t in range(comp.Segments):
                tags[t] = system.particles.add(comp.Name)
                system.particles[tags[t]].diameter = 1.0
                system.particles[tags[t]].type = comp.Name
            newTags.append(tags)
            for t in range(comp.Segments-1):
                system.bonds.add(comp.BondName,tags[t],tags[t+1])
            for t in range(comp.Segments-2):
                system.angles.add(comp.AngleName,tags[t],tags[t+1],tags[t+2])
    return newTags

def placeRandomly(moleculeList,system,comp):
    # Place randomly with each segment in a line
    Lx, Ly, Lz = (system.box.Lx, system.box.Ly, system.box.Lz)
    dz = comp.Sigma 
    # Loop over list of molecules
    for m in moleculeList:
        # Pick three random numbers, any numbers
        rand1 = uniform(-0.4999,0.4999)
        rand2 = uniform(-0.4999,0.4999)
        rand3 = uniform(-0.4999,0.4999-(len(m)*dz)/Lz)
        r = ( rand1*Lx, rand2*Ly, rand3*Lz ) # Leave space for the chain
        # Set the positions
        for i,p in enumerate(m):
            q = system.particles[p] 
            q.position = ( r[0], r[1], r[2] + i*dz )

def initMiePotential(table=False):
    if table:
        mie = pair.table(width=1000)
        mie.isTable = True
    else:
        try:
            # HOOMD 1.1 and later offer a mie potential. Use it if present,
            # otherwise fall back to table.
            # Dummy cutoff, required here, will be overridden
            mie = pair.mie(r_cut=20.0)
            # Set variable telling other functions that this is available
            mie.isTable = False
        except Exception as e:
            print(e)
            mie = pair.table(width=1000)
            mie.isTable = True
    return mie


def setupAngles(system,components):
    for comp in components:
        # Set the group for each component
        comp.Group = getGroup(comp)
        # If the component has any angles, add them
        if comp.Segments > 2:
            comp.createAngles(system)

def setMasses(system,components):
    snap = system.take_snapshot(all=True)
    compMassDict = { sc.Name: sc.Mass for sc in getAllSubComponents(components) }
    for i in range(len(snap.particles.mass)):
        name = snap.particles.types[snap.particles.typeid[i]]
        snap.particles.mass[i] = compMassDict[name] 
    system.restore_snapshot(snap)

def setDiameters(system,components):
    snap = system.take_snapshot(all=True)
    compDiamDict = { sc.Name: sc.Sigma for sc in getAllSubComponents(components) }
    for i in range(len(snap.particles.diameter)):
        name = snap.particles.types[snap.particles.typeid[i]]
        snap.particles.diameter[i] = compDiamDict[name]
    system.restore_snapshot(snap)

# The following routines gmx* write input files for GROMACS. the
# writeGromacsFiles() routine simply calls all of them.
#
# The units in GROMACS are slightly different than those we use. Compare tables
# 2.1 and 2.2 in the GROMACS manual with tables 1 and 2 in the raaSAFT paper.

def writeGromacsFiles(system,components):
    gmxWriteITP(system,components)
    gmxWriteAllXVG(system,components)
    gmxWriteGRO(system,components)
    gmxWriteTOP(system,components)
    gmxWriteMDP(system,components)

def gmxWriteXVG(name,n,m,rmax):
    # This writes one XVG file for one potential (combination of exponents m,n)
    # that we want to use. We iterate over the components and cross-interactions
    # and write all these in gmxWriteAllXVG() below.
    filename = 'table_' + name.upper() + '.xvg'
    # Scale rmax for nm instead of Å
    rmax = rmax/10.0
    c_mie = (n / (n - m)) * (n / m) ** (m / (n - m))
    with open(filename, 'w') as xvg:
        xvg.write('# Tabulated Mie potential, generated by raaSAFT\n')
        xvg.write('# The exponents are n=' + str(n) + ' and m=' + str(m) + '\n')
        xvg.write('# Please calculate your A = ' + str(c_mie) + ' x Epsilon x Sigma^' + str(n) + ' and C = ' + str(c_mie) + ' x Epsilon x Sigma^' + str(m) + '\n')
        # Write first line for r=0
        xvg.write('{:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}\n'.format(0, 0, 0, 0, 0, 0, 0))
        # Then loop until cutoff and do the rest of the table
        r = 0.0
        while r < rmax + 1:
            r += 0.002
            f = 1 / r
            fprime = 1 / r ** 2
            g = -1 / r ** m
            gprime = -m / r ** (m + 1)
            h = 1 / r ** n
            hprime = n / r ** (n + 1)
            if hprime > 1e+27:
                xvg.write('{:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}\n'.format(r, 0, 0, 0, 0, 0, 0))
            else:
                xvg.write('{:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}   {:12.10e} {:12.10e}\n'.format(r, f, fprime, g, gprime, h, hprime))

def gmxWriteAllXVG(system, components):
    # Do all components
    components = getAllSubComponents(components)
    for comp in components:
        name = comp.Name + "_" + comp.Name
        gmxWriteXVG(name,comp.N,comp.M,comp.RMax)
    # Then do all cross interactions
    for A,B in combinations(components,2):
        # Lafitte rules
        nAB = 3 + sqrt((A.N-3)*(B.N-3))
        mAB = 3 + sqrt((A.M-3)*(B.M-3))
        name = A.Name + "_" + B.Name
        rmax = max(A.RMax,B.RMax)
        # Write
        gmxWriteXVG(name,nAB,mAB,rmax)
    # Finally, copy one of the XVG files to "table.xvg". This makes the GROMACS
    # command line shorter, apparently.
    copyfile("table_"+components[0].Name.upper()+"_"+components[0].Name.upper()+".xvg", "table.xvg")

def gmxWriteITP(system,components):
    # This writes an ITP file for GROMACS. This file contains all component
    # layouts, as well as subcomponent specifications.
    filename = str(sys.argv[0].rsplit('.', 1)[0]) + '.itp'
    with open(filename, 'w') as itp:
        itp.write('[ atomtypes ]\n')
        itp.write('; This file was generated by raaSAFT on ' + datetime.now().strftime('%d %b %Y, %H:%M:%S') + '\n')
        itp.write(';\n')
        itp.write('; name  bond_type     mass      charge   ptype   C             A\n')
        for comp in getAllSubComponents(components):
            c_mie = (comp.N / (comp.N - comp.M)) * (comp.N / comp.M) ** (comp.M / (comp.N - comp.M))
            # Scale units
            epsilon = comp.Epsilon/100.0
            sigma = comp.Sigma/10.0
            comp_C = c_mie * epsilon * sigma ** comp.N
            comp_A = c_mie * epsilon * sigma ** comp.M
            if comp.Segments > 2:
                bond_type = 'C'
            else:
                bond_type = 'H'
            mass = comp.Mass
            itp.write('{0:^10} {1:<10} {2:2.5f}   0.000    A      {3:e} {4:e}\n'.format(comp.Name[0:5].upper(), bond_type, mass, comp_C, comp_A))
        
        itp.write('\n')
        itp.write('[ nonbond_params ]\n')
        itp.write('; these are the crossinteractions\n')
        itp.write('; i         j          func     C             A\n')
        for (A, B) in combinations(getAllSubComponents(components), 2):
            # Scale units
            asig = A.Sigma/10.0
            bsig = B.Sigma/10.0
            aeps = A.Epsilon/100.0
            beps = B.Epsilon/100.0
            # Compute cross interaction from Lafitte rules
            SigmaAB = 0.5 * (asig + bsig)
            nAB = 3 + sqrt((A.N - 3) * (B.N - 3))
            mAB = 3 + sqrt((A.M - 3) * (B.M - 3))
            # Get the kij, default to zero if nothing set by user.
            kAB = A.kij.get(B.Name,0.0)
            EpsilonAB = (1.0 - kAB) * (sqrt(asig * bsig) / SigmaAB) ** 3 * sqrt(aeps * beps)
            c_mie = (nAB / (nAB - mAB)) * (nAB / mAB) ** (mAB / (nAB - mAB))
            cross_C = c_mie * EpsilonAB * SigmaAB ** nAB
            cross_A = c_mie * EpsilonAB * SigmaAB ** mAB
            itp.write('{0:<7} {1:<7}  1        {2:e}  {3:e}\n'.format(A.Name[0:5].upper(), B.Name[0:5].upper(), cross_C, cross_A))
        
        itp.write('\n')
        for comp in components:
            itp.write('[ moleculetype ]\n')
            itp.write('; Name    nrexcl\n')
            # Double check that we never need nrexcl != 1
            itp.write('{0:<7}  1\n'.format(comp.Name[0:5].upper()))
            itp.write('\n')
            itp.write('[ atoms ]\n')
            itp.write('; nr type  resnr residue  atom      cgnr\n')
            tcount = 0
            lasttype = ''
            atom = 0
            for t in comp.Types:
                tcount += 1
                if lasttype != t:
                    lasttype = t
                    atom += 1
                itp.write('{0:>3}  {1:<7}  1  {2:<7}  {3:<7}  {4:>3}      \n'.format(tcount, t[0:5].upper(), comp.Name[0:5].upper(), t[0:5].upper(), atom))
            
            itp.write('\n')
            if comp.Segments > 1:
                bonds = [ (a + 1, b + 1, name) for (a, b, name) in comp.Bonds ]
                bondsfull = []
                for a, b, name in bonds:
                    # Underscore is a throwaway variable, since we don't need the name again
                    _, kbo, b0 = next( bs for bs in comp.BondSpec if bs[0] == name )
                    # Unit scaling
                    b0 = b0/10.0
                    kbo = kbo/2.0 # factor of 2 difference in potential def.
                    # Put it in the list
                    bondsfull.append((a, b, b0, kbo))
                
                itp.write('[ bonds ]\n')
                itp.write(';\tai\taj   funct      bo       kbo\n')
                for bond in bondsfull:
                    itp.write('{0:<4} {1:<4}   1        {2:7.5f} {3:7.1f}\n'.format(*bond))
                
                itp.write('\n')
            if comp.Segments > 2:
                try:
                    angles = [ (a + 1, b + 1, c + 1, name) for (a, b, c, name) in comp.Angles ]
                except AttributeError:
                    # This component doesn't have angles, so skip it
                    pass
                else:
                    # It has angles, handle them
                    anglesfull = []
                    for a, b, c, name in angles:
                        _, kan, an0 = next( ans for ans in comp.AngleSpec if ans[0] == name )
                        # Unit scaling
                        an0 = an0 * 180.0 / pi
                        kan = kan/(2.0*100.0) # Factor of 2 from def. and 100 from units
                        # Put it in the list
                        anglesfull.append((a, b, c, an0, kan))
                    itp.write('[ angles ]\n')
                    itp.write(';ai  aj   ak    funct     angle    Kangle\n')
                    for angle in anglesfull:
                        itp.write('{0:<4} {1:<4} {2:<4}   1        {3:<4}    {4}\n'.format(*angle))
                    
                    itp.write('\n')
            # Dihedrals would go here if we supported them
            # That's the end of this component, loop will continue with next component
        # And that's the end of the file

def gmxWriteGRO(system,components):
    # This writes a GRO file for GROMACS. This file contains all the bead
    # numbers, types, initial positions etc. 
    filename = str(sys.argv[0].rsplit('.', 1)[0]) + '.gro'
    snap = system.take_snapshot()
    # Create a dictionary that maps from subcomponent names to component names
    subCompNames = dict()
    for comp in components:
        for scomp in subComps(comp):
            # Sanity check
            if scomp.Name in subCompNames:
                print("Subcomponents names are not unique! This not supported.")
                error("Ensure all heteronuclears have unique shortnames.")
            # If no error, set the entry
            subCompNames[scomp.Name] = comp
    
    with open(filename, 'w') as gro:
        # Get the total number of beads
        numberofbeads = sum(c.Count*c.Segments for c in components)
        # Python magic. This gives e.g. "BioWater, Cyclohexane, C12"
        systemnames = ", ".join(c.Name for c in components)
        # Write the header. First line is system description, then # of beads
        gro.write('raaSAFT generated file, contains '+systemnames+"\n")
        gro.write('{0:5d}\n'.format(numberofbeads))
        # Set initial values of various counters that we need
        molnumber = 0
        numberinmol = 0
        segprev = 1
        # Then write a line for each bead with the information:
        # moleculename beadtype beadnumber x y z vx vy vz
        for i in range(len(snap.particles.mass)):
            # Much computation of all the things we need
            # Get the current subcomponent name
            scname = snap.particles.types[snap.particles.typeid[i]]
            # Get the current component name
            mol = subCompNames[scname]
            # Increment what number this bead has in this molecule
            numberinmol = numberinmol%segprev + 1
            # Set the segment number for use in the next iteration
            segprev = mol.Segments
            # Increment the molecule number if this is the start of a new one
            if numberinmol == 1:
                molnumber = molnumber + 1
            # Get the molecule name, only first 5 characters, left justified and space padded
            molname = mol.Name[0:5].ljust(5)
            # Make the subcomponent name have only 5 characters, right justified
            scname = scname[0:5].rjust(5)
            # Get position and velocity, scale to GROMACS units
            x, y, z = [ pos/10.0 for pos in snap.particles.position[i] ]
            vx, vy, vz = [ vel/10.0 for vel in snap.particles.velocity[i] ]
            # Then write the line. i+1 since GROMACS is 1-indexed.
            gro.write("{0:5d}{1:<}{2:<}{3:5d}{4:8.3f}{5:8.3f}{6:8.3f}{7:8.4f}{8:8.4f}{9:8.4f}\n".format(molnumber,molname.upper(),scname.upper(),i+1,x,y,z,vx,vy,vz))
        # Finally, write the box dimensions on the last line.
        Lx = snap.box.Lx/10
        Ly = snap.box.Ly/10
        Lz = snap.box.Lz/10
        gro.write("{0:10.5f}{1:10.5f}{2:10.5f}\n".format(Lx,Ly,Lz))
    # That's the end of the file

def gmxWriteTOP(system,components):
    filename = 'system.top'
    ITPname = str(sys.argv[0].rsplit('.', 1)[0]) + '.itp'
    with open(filename, 'w') as top:
        top.write("[ defaults ]\n")
        top.write("; nbfunc comb-rule gen-pairs fudgeLJ fudgeQQ\n")
        top.write("  1      1         \n")
        top.write("\n")
        top.write('#include "'+ITPname+'"\n')
        top.write("\n")
        # Generate contents of system
        top.write("[ system ]\n")
        systemnames = ", ".join(c.Name for c in components)
        top.write('raaSAFT generated file, contains '+systemnames+"\n")
        top.write("\n")
        top.write("[ molecules ]\n")
        for comp in components:
            name = comp.Name[0:5].ljust(5)
            top.write("{0:<} {1:>6}\n".format(name.upper(),comp.Count))
    # End of file

def gmxWriteMDP(system,components):
    filename = 'NVT.mdp'
    # Create group string and (cross-)interaction strings
    allSubComps = getAllSubComponents(components)
    groups = " ".join( c.Name[0:5].upper() for c in allSubComps )
    Ngroups = len(allSubComps)
    interactions = " ".join( a.Name[0:5].upper()+" "+b.Name[0:5].upper() for a,b in combinations_with_replacement(allSubComps,2) )
    # Cutoff should be set to the same for all, so just use first in list
    cutoff = "{0:4.2f}".format(components[0].RMax/10.0)
    print(cutoff)
    with open(filename, 'w') as mdp:
        mdp.write("; VARIOUS PREPROCESSING OPTIONS = \n")
        mdp.write("include                  = \n")
        mdp.write("define                   = -DPOSRES\n")
        mdp.write("; RUN CONTROL PARAMETERS = \n")
        mdp.write("integrator               = md\n")
        mdp.write("; start time and timestep in ps = \n")
        mdp.write("tinit                    = 0\n")
        mdp.write("dt                       = 0.01\n")
        mdp.write("nsteps                   = 980000\n")
        mdp.write("; For exact run continuation or redoing part of a run\n")
        mdp.write("init_step                = 0\n")
        mdp.write("; number of steps for center of mass motion removal = \n")
        mdp.write("nstcomm                  = 1\n")
        mdp.write("comm_grps		 =\n")
        mdp.write("\n")
        mdp.write("; OUTPUT CONTROL OPTIONS = \n")
        mdp.write("; Output frequency for coords (x), velocities (v) and forces (f) = \n")
        mdp.write("nstxout                  = 1000\n")
        mdp.write("nstvout                  = 1000\n")
        mdp.write("nstfout                  = 1000\n")
        mdp.write("; Output frequency for energies to log file and energy file = \n")
        mdp.write("nstlog                   = 1000\n")
        mdp.write("nstenergy                = 1000 \n")
        mdp.write("; Output frequency and precision for xtc file = \n")
        mdp.write("nstxtcout                = 1000\n")
        mdp.write("xtc-precision            = 1000\n")
        mdp.write("; This selects the subset of atoms for the xtc file. You can = \n")
        mdp.write("; select multiple groups. By default all atoms will be written. = \n")
        mdp.write("xtc-grps                 = \n")
        mdp.write("; Selection of energy groups = \n")
        mdp.write("energygrps               = "+groups+"\n")
        mdp.write("energygrp_table          = "+interactions+" ;all interactions that you want (and crossinteractions)\n")
        mdp.write("\n")
        mdp.write("; NEIGHBORSEARCHING PARAMETERS = \n")
        mdp.write("cutoff-scheme             = group\n")
        mdp.write("; nblist update frequency = \n")
        mdp.write("nstlist                  = 5\n")
        mdp.write("; ns algorithm (simple or grid) = \n")
        mdp.write("ns-type                  = grid\n")
        mdp.write("pbc			 = xyz \n")
        mdp.write("; nblist cut-off         = \n")
        mdp.write("rlist                    = "+cutoff+"\n")
        mdp.write("\n")
        mdp.write("; OPTIONS FOR ELECTROSTATICS AND VDW = \n")
        mdp.write("; Method for doing electrostatics = \n")
        mdp.write("coulombtype              = user\n")
        mdp.write("rcoulomb-switch          = 0\n")
        mdp.write("rcoulomb                 = "+cutoff+"\n")
        mdp.write("; Dielectric constant (DC) for cut-off or DC of reaction field = \n")
        mdp.write("epsilon-r                = 1\n")
        mdp.write("; Method for doing Van der Waals = \n")
        mdp.write("vdwtype                  = user\n")
        mdp.write("; cut-off lengths        = \n")
        mdp.write("rvdw-switch              = 0\n")
        mdp.write("rvdw                     = "+cutoff+"\n")
        mdp.write("; Apply long range dispersion corrections for Energy and Pressure = \n")
        mdp.write("DispCorr                 = no \n")
        mdp.write("; Spacing for the PME/PPPM FFT grid = \n")
        mdp.write("fourierspacing           = 0.12\n")
        mdp.write("; FFT grid size, when a value is 0 fourierspacing will be used = \n")
        mdp.write("fourier_nx               = 0\n")
        mdp.write("fourier_ny               = 0\n")
        mdp.write("fourier_nz               = 0\n")
        mdp.write("; EWALD/PME/PPPM parameters = \n")
        mdp.write("pme_order                = 4\n")
        mdp.write("ewald_rtol               = 1e-05\n")
        mdp.write("\n")
        mdp.write("; OPTIONS FOR WEAK COUPLING ALGORITHMS = \n")
        mdp.write("; Temperature coupling   = \n")
        mdp.write("tcoupl                   = nose-hoover\n")
        mdp.write("; Groups to couple separately = \n")
        mdp.write("tc-grps                  = "+groups+"\n")
        mdp.write("; Time constant (ps) and reference temperature (K) = \n")
        mdp.write("tau-t                    = "+"1.0 "*Ngroups+" \n")
        mdp.write("ref-t                    = "+"298.15 "*Ngroups+" \n")
        mdp.write("; Pressure coupling      = \n")
        mdp.write("pcoupl                   = no\n")
        mdp.write("pcoupltype               = isotropic\n")
        mdp.write("; Time constant (ps), compressibility (1/bar) and reference P (bar) = \n")
        mdp.write("tau-p                    = "+"1.0 "*Ngroups+" \n")
        mdp.write("compressibility          = "+"4.50E-5 "*Ngroups+" \n")
        mdp.write("ref-p                    = "+"1.01325 "*Ngroups+" \n")
        mdp.write("\n")
        mdp.write("; SIMULATED ANNEALING CONTROL = \n")
        mdp.write("annealing                = no\n")
        mdp.write("\n")
        mdp.write("; GENERATE VELOCITIES FOR STARTUP RUN = \n")
        mdp.write("gen-vel                  = no\n")
        mdp.write("gen-temp                 = 293.15\n")
        mdp.write("gen-seed                 = 173539\n")
        mdp.write("\n")
        mdp.write("; Convert harmonic bonds to morse potentials = \n")
        mdp.write("morse                    = no\n")
        mdp.write("\n")
        mdp.write("; NMR refinement stuff  = \n")
        mdp.write("; Distance restraints type: No, Simple or Ensemble = \n")
        mdp.write("disre                    = simple \n")
        mdp.write("; Force weighting of pairs in one distance restraint: Equal or Conservative = \n")
        mdp.write("disre-weighting          = conservative \n")
        mdp.write("; Use sqrt of the time averaged times the instantaneous violation = \n")
        mdp.write("disre-mixed              = no\n")
        mdp.write("disre-fc                 = 1\n")
        mdp.write("disre-tau                = 0\n")
        mdp.write("; Output frequency for pair distances to energy file = \n")
        mdp.write("nstdisreout              = 1000\n")
        mdp.write("\n")
        mdp.write("; Free energy control stuff = \n")
        mdp.write("free-energy              = no\n")
        mdp.write("init-lambda              = 0\n")
        mdp.write("delta-lambda             = 0\n")
        mdp.write("sc_alpha                 = 0\n")
        mdp.write("sc_sigma                 = 0.3\n")
        mdp.write("\n")
        mdp.write("; Non-equilibrium MD stuff = \n")
        mdp.write("acc-grps                 = \n")
        mdp.write("accelerate               = \n")
        mdp.write("freezegrps               = \n")
        mdp.write("freezedim                = \n")
        mdp.write("cos_acceleration         = \n")
        mdp.write("\n")
        mdp.write("; Electric fields        = \n")
        mdp.write("; Format is number of terms (int) and for all terms an amplitude (real) = \n")
        mdp.write("; and a phase angle (real) = \n")
        mdp.write("E-x                      = \n")
        mdp.write("E-xt                     = \n")
        mdp.write("E-y                      = \n")
        mdp.write("E-yt                     = \n")
        mdp.write("E-z                      = \n")
        mdp.write("E-zt                     = \n")
        mdp.write("\n")
        mdp.write("; User defined parameters go here\n")
        mdp.write("\n")
        # End of file
