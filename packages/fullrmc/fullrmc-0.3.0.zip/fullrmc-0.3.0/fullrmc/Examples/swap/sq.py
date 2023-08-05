# standard libraries imports
import os

# external libraries imports
import numpy as np
import matplotlib.pyplot as plt

# fullrmc library imports
from fullrmc.Engine import Engine
from fullrmc.Constraints.PairCorrelationConstraints import PairCorrelationConstraint


# engine variables
engineSavePath = "engine.rmc"
    
# check Engine already saved
if engineSavePath not in os.listdir("."):
    exit()
else:
    ENGINE = Engine(pdb=None).load(engineSavePath)
    PCF = PairCorrelationConstraint(engine=None, experimentalData="experimental.gr", weighting="atomicNumber")
    ENGINE.add_constraints([PCF]) 
    PCF.compute_data()
      
      
def get_sq(distances, gr, qrange, rho):
    # s(q) = 1+4*pi*Rho*INTEGRAL[r * g(r) * sin(qr)/q * dr]
    dr = distances[1]-distances[0]
    sq = np.zeros(len(qrange))
    for qidx in range(len(qrange)):
        q = qrange[qidx]
        for ridx in range(len(distances)):
            r = distances[ridx]
            sq[qidx] += dr*r*(np.sin(q*r)/q)*(gr[ridx]-1)
    return 1 + 4*np.pi*rho*sq


# compute sq
rho    = len(ENGINE.pdb)/ENGINE.boundaryConditions.get_box_volume()
qrange = np.arange(0.01, 20, 0.01)
output = PCF.get_constraint_value()
sq = get_sq(distances=PCF.shellsCenter, gr=output["pcf"], qrange=qrange, rho=rho)


plt.plot(qrange, sq, label="sq from pair correlation function")
plt.legend()
plt.show()
 
 

        
 