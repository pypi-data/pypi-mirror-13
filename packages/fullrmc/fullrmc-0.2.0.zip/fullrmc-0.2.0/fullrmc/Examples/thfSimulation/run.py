# standard libraries imports
import os

# external libraries imports
import numpy as np

# fullrmc library imports
from fullrmc.Globals import LOGGER, FLOAT_TYPE
from fullrmc.Engine import Engine
from fullrmc.Constraints.PairDistributionConstraints import PairDistributionConstraint
from fullrmc.Constraints.PairCorrelationConstraints import PairCorrelationConstraint
from fullrmc.Constraints.DistanceConstraints import InterMolecularDistanceConstraint
from fullrmc.Constraints.BondConstraints import BondConstraint
from fullrmc.Constraints.AngleConstraints import BondsAngleConstraint
from fullrmc.Constraints.ImproperAngleConstraints import ImproperAngleConstraint
from fullrmc.Core.Collection import convert_Gr_to_gr
from fullrmc.Core.MoveGenerator import MoveGeneratorCollector
from fullrmc.Core.GroupSelector import RecursiveGroupSelector
from fullrmc.Selectors.RandomSelectors import RandomSelector
from fullrmc.Selectors.OrderedSelectors import DefinedOrderSelector
from fullrmc.Generators.Translations import TranslationGenerator, TranslationAlongSymmetryAxisGenerator
from fullrmc.Generators.Rotations import RotationGenerator, RotationAboutSymmetryAxisGenerator
from fullrmc.Generators.Agitations import DistanceAgitationGenerator, AngleAgitationGenerator

# dirname
DIR_PATH = os.path.dirname( os.path.realpath(__file__) )

# engine file names
engineFileName = "thf_engine.rmc"
expFileName    = "thf_pdf.exp"
pdbFileName    = "thf.pdb" 

# engine variables
expPath        = os.path.join(DIR_PATH, expFileName)
pdbPath        = os.path.join(DIR_PATH, pdbFileName)
engineFilePath = os.path.join(DIR_PATH, engineFileName)
    
# check Engine already saved
if engineFileName not in os.listdir(DIR_PATH):
    CONSTRUCT = True
else:
    CONSTRUCT = False
  
# construct and save engine or load engine
if CONSTRUCT:
    # initialize engine
    ENGINE = Engine(pdb=pdbPath, constraints=None)
    # create constraints
    #PDF_CONSTRAINT = PairDistributionConstraint(engine=None, experimentalData=expPath, weighting="atomicNumber")
    _,_,_, gr = convert_Gr_to_gr(np.loadtxt(expPath), minIndex=[4,5,6])
    dataWeights = np.ones(gr.shape[0])
    dataWeights[:np.nonzero(gr[:,1]>0)[0][0]] = 0  
    PDF_CONSTRAINT = PairCorrelationConstraint(engine=None, experimentalData=gr.astype(FLOAT_TYPE), weighting="atomicNumber", dataWeights=dataWeights)
    EMD_CONSTRAINT = InterMolecularDistanceConstraint(engine=None)
    B_CONSTRAINT   = BondConstraint(engine=None)
    BA_CONSTRAINT  = BondsAngleConstraint(engine=None)
    IA_CONSTRAINT  = ImproperAngleConstraint(engine=None)
    # add constraints to engine
    ENGINE.add_constraints([PDF_CONSTRAINT, EMD_CONSTRAINT, B_CONSTRAINT, BA_CONSTRAINT, IA_CONSTRAINT])
    # initialize constraints definitions
    B_CONSTRAINT.create_bonds_by_definition( bondsDefinition={"THF": [('O' ,'C1' , 1.29, 1.70),
                                                                      ('O' ,'C4' , 1.29, 1.70),
                                                                      ('C1','C2' , 1.29, 1.70),
                                                                      ('C2','C3' , 1.29, 1.70),
                                                                      ('C3','C4' , 1.29, 1.70),
                                                                      ('C1','H11', 0.58, 1.15),('C1','H12', 0.58, 1.15),
                                                                      ('C2','H21', 0.58, 1.15),('C2','H22', 0.58, 1.15),
                                                                      ('C3','H31', 0.58, 1.15),('C3','H32', 0.58, 1.15),
                                                                      ('C4','H41', 0.58, 1.15),('C4','H42', 0.58, 1.15)] })
    BA_CONSTRAINT.create_angles_by_definition( anglesDefinition={"THF": [ ('O'  ,'C1' ,'C4' , 100 , 130),
                                                                          ('C1' ,'O'  ,'C2' , 100 , 130),
                                                                          ('C4' ,'O'  ,'C3' , 100 , 130),
                                                                          ('C2' ,'C1' ,'C3' , 95 , 115),
                                                                          ('C3' ,'C2' ,'C4' , 95 , 115),
                                                                          # H-C-H angle
                                                                          ('C1' ,'H11','H12', 98 , 118),
                                                                          ('C2' ,'H21','H22', 98 , 118),
                                                                          ('C3' ,'H31','H32', 98 , 118),
                                                                          ('C4' ,'H41','H42', 98 , 118),
                                                                          # H-C-O angle
                                                                          ('C1' ,'H11','O'  , 100, 120),
                                                                          ('C1' ,'H12','O'  , 100, 120),
                                                                          ('C4' ,'H41','O'  , 100, 120),
                                                                          ('C4' ,'H42','O'  , 100, 120),                                                                           
                                                                          # H-C-C
                                                                          ('C1' ,'H11','C2' , 90, 110),
                                                                          ('C1' ,'H12','C2' , 90, 110),
                                                                          ('C2' ,'H21','C1' , 90, 110),
                                                                          ('C2' ,'H21','C3' , 90, 110),
                                                                          ('C2' ,'H22','C1' , 90, 110),
                                                                          ('C2' ,'H22','C3' , 90, 110),
                                                                          ('C3' ,'H31','C2' , 90, 110),
                                                                          ('C3' ,'H31','C4' , 90, 110),
                                                                          ('C3' ,'H32','C2' , 90, 110),
                                                                          ('C3' ,'H32','C4' , 90, 110),
                                                                          ('C4' ,'H41','C3' , 90, 110),
                                                                          ('C4' ,'H42','C3' , 90, 123) ] })
    IA_CONSTRAINT.create_angles_by_definition( anglesDefinition={"THF": [ ('C2','O','C1','C4', -15, 15),
                                                                          ('C3','O','C1','C4', -15, 15) ] })
    # initialize constraints data
    PDF_CONSTRAINT.set_used(True)
    EMD_CONSTRAINT.set_used(True)
    B_CONSTRAINT.set_used(True)
    BA_CONSTRAINT.set_used(True)
    IA_CONSTRAINT.set_used(True)
    ENGINE.initialize_used_constraints()
    # save engine
    ENGINE.save(engineFilePath)
else:
    ENGINE = Engine(pdb=None).load(engineFilePath)
    
    
    
# ############ RUN C-H BONDS ############ #
def bonds_CH(ENGINE, rang=10, recur=10, refine=False, explore=True, exportPdb=False): 
    groups = []
    for idx in range(0,ENGINE.pdb.numberOfAtoms, 13):
        groups.append( np.array([idx+1 ,idx+2 ], dtype=np.int32) ) # C1-H11
        groups.append( np.array([idx+1 ,idx+3 ], dtype=np.int32) ) # C1-H12
        groups.append( np.array([idx+4 ,idx+5 ], dtype=np.int32) ) # C2-H21
        groups.append( np.array([idx+4 ,idx+6 ], dtype=np.int32) ) # C2-H22
        groups.append( np.array([idx+7 ,idx+8 ], dtype=np.int32) ) # C3-H31
        groups.append( np.array([idx+7 ,idx+9 ], dtype=np.int32) ) # C3-H32
        groups.append( np.array([idx+10,idx+11], dtype=np.int32) ) # C4-H41
        groups.append( np.array([idx+10,idx+12], dtype=np.int32) ) # C4-H42
    ENGINE.set_groups(groups)
    [g.set_move_generator(DistanceAgitationGenerator(amplitude=0.2,agitate=(True,True))) for g in ENGINE.groups]
    # set selector
    if refine or explore:
        gs = RecursiveGroupSelector(RandomSelector(ENGINE), recur=recur, refine=refine, explore=explore)
        ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'bonds_CH' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%i_bonds_CH.pdb"%(ENGINE.generated)) )

# ############ RUN H-C-H ANGLES ############ #   
def angles_HCH(ENGINE, rang=5, recur=10, refine=False, explore=True, exportPdb=False):  
    groups = []
    for idx in range(0,ENGINE.pdb.numberOfAtoms, 13):
        groups.append( np.array([idx+1 ,idx+2, idx+3 ], dtype=np.int32) ) # H11-C1-H12
        groups.append( np.array([idx+4 ,idx+5, idx+6 ], dtype=np.int32) ) # H21-C2-H22
        groups.append( np.array([idx+7 ,idx+8, idx+9 ], dtype=np.int32) ) # H31-C3-H32
        groups.append( np.array([idx+10,idx+11,idx+12], dtype=np.int32) ) # H41-C4-H42
    ENGINE.set_groups(groups)   
    [g.set_move_generator(AngleAgitationGenerator(amplitude=5)) for g in ENGINE.groups] 
    # set selector
    if refine or explore:
        gs = RecursiveGroupSelector(RandomSelector(ENGINE), recur=recur, refine=refine, explore=explore)
        ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'angles_HCH' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%i_angles_HCH.pdb"%(ENGINE.generated)) )    

# ############ RUN ATOMS ############ #    
def atoms(ENGINE, rang=30, recur=20, refine=False, explore=True, exportPdb=False):
    ENGINE.set_groups_as_atoms()  
    # set selector
    if refine or explore:
        gs = RecursiveGroupSelector(RandomSelector(ENGINE), recur=recur, refine=refine, explore=explore)
        ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'atoms' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%i_atoms.pdb"%(ENGINE.generated)) )    
     
# ############ RUN ROTATION ABOUT SYMM AXIS 0 ############ #
def about0(ENGINE, rang=5, recur=100, refine=True, explore=False, exportPdb=False):  
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(axis=0, amplitude=180)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'about0' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_about0.pdb"%(ENGINE.generated)) ) 
 
# ############ RUN ROTATION ABOUT SYMM AXIS 1 ############ #
def about1(ENGINE, rang=5, recur=10, refine=True, explore=False, exportPdb=False):  
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(axis=1, amplitude=180)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'about1' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_about1.pdb"%(ENGINE.generated)) )    
        
# ############ RUN ROTATION ABOUT SYMM AXIS 2 ############ #
def about2(ENGINE, rang=5, recur=100, refine=True, explore=False, exportPdb=False): 
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(RotationAboutSymmetryAxisGenerator(axis=2, amplitude=180)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'about2' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_about2.pdb"%(ENGINE.generated)) )  

# ############ RUN TRANSLATION ALONG SYMM AXIS 0 ############ #
def along0(ENGINE, rang=5, recur=100, refine=False, explore=True, exportPdb=False):  
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(TranslationAlongSymmetryAxisGenerator(axis=0, amplitude=0.1)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'along0' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_along0.pdb"%(ENGINE.generated)) )    

# ############ RUN TRANSLATION ALONG SYMM AXIS 1 ############ #
def along1(ENGINE, rang=5, recur=100, refine=False, explore=True, exportPdb=False):  
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(TranslationAlongSymmetryAxisGenerator(axis=1, amplitude=0.1)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    recur = 200
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'along1' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_along1.pdb"%(ENGINE.generated)) )    

# ############ RUN TRANSLATION ALONG SYMM AXIS 2 ############ # 
def along2(ENGINE, rang=5, recur=100, refine=False, explore=True, exportPdb=False):   
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator(TranslationAlongSymmetryAxisGenerator(axis=2, amplitude=0.1)) for g in ENGINE.groups]
    # set selector
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(rang):
        LOGGER.info("Running 'along2' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_along2.pdb"%(ENGINE.generated)) )    

# ############ RUN MOLECULES ############ #
def molecules(ENGINE, rang=5, recur=100, refine=False, explore=True, exportPdb=False):
    ENGINE.set_groups_as_molecules()
    [g.set_move_generator( MoveGeneratorCollector(collection=[TranslationGenerator(amplitude=0.2),RotationGenerator(amplitude=2)],randomize=True) ) for g in ENGINE.groups]
    # number of steps
    nsteps = 20*len(ENGINE.groups)
    # set selector
    gs = RecursiveGroupSelector(RandomSelector(ENGINE), recur=recur, refine=refine, explore=explore)
    ENGINE.set_group_selector(gs)
    for stepIdx in range(rang):
        LOGGER.info("Running 'molecules' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%i_molecules.pdb"%(ENGINE.generated)) )

# ############ SHRINK SYSTEM ############ #   
def shrink(ENGINE, newDim, exportPdb=False):
    ENGINE.set_groups_as_molecules()  
    # get groups order    
    centers   = [np.sum(ENGINE.realCoordinates[g.indexes], axis=0)/len(g) for g in ENGINE.groups]
    distances = [np.sqrt(np.add.reduce(c**2)) for c in centers]
    order     = np.argsort(distances)
    [g.set_move_generator( MoveGeneratorCollector(collection=[TranslationGenerator(amplitude=0.2),RotationGenerator(amplitude=5)],randomize=True) ) for g in ENGINE.groups]
    # change boundary conditions
    bcFrom = str([list(bc) for bc in ENGINE.boundaryConditions.get_vectors()] )
    ENGINE.set_boundary_conditions(newDim)
    bcTo   = str([list(bc) for bc in ENGINE.boundaryConditions.get_vectors()] )
    LOGGER.info("boundary conditions changed from %s to %s"%(bcFrom,bcTo))
    # set selector
    recur = 200
    gs = RecursiveGroupSelector(DefinedOrderSelector(ENGINE, order = order ), recur=recur, refine=True)
    ENGINE.set_group_selector(gs)
    # number of steps
    nsteps = recur*len(ENGINE.groups)
    for stepIdx in range(10):
        LOGGER.info("Running 'shrink' mode step %i"%(stepIdx))
        ENGINE.run(numberOfSteps=nsteps, saveFrequency=nsteps, savePath=engineFilePath)
        fname = "shrink_"+str(newDim).replace(".","p")
        if exportPdb:
            ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%s_%s.pdb"%(ENGINE.generated, fname)) )    


# tweak constraints
PDF_CONSTRAINT, EMD_CONSTRAINT, B_CONSTRAINT, BA_CONSTRAINT, IA_CONSTRAINT = ENGINE.constraints


# ############ RUN ENGINE ############ #
#ENGINE.export_pdb( os.path.join(DIR_PATH, "pdbFiles","%i_original.pdb"%(ENGINE.generated)) )
bonds_CH(ENGINE)
angles_HCH(ENGINE)
atoms(ENGINE, explore=False, refine=False)
# refine scaling factor
PDF_CONSTRAINT.set_adjust_scale_factor((10, 0.8, 1.2)) 
atoms(ENGINE, explore=True, refine=False)
about0(ENGINE)
about1(ENGINE)
about2(ENGINE)
along0(ENGINE)
along1(ENGINE)
along2(ENGINE)
molecules(ENGINE)
atoms(ENGINE, explore=True, refine=False)

