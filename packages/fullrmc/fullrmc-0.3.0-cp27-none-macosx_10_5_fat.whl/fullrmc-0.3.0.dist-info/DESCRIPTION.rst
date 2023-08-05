fullrmc is a Reverse Monte Carlo (RMC) modelling package.
RMC is probably best known for its applications in condensed matter physics and solid state chemistry.
RMC is used to solve an inverse problem whereby an atomic/molecular model is adjusted until its atoms position have the greatest consistency with a set of experimental data.
fullrmc is a python package with its core and calculation modules optimized and compiled in Cython.
fullrmc is not a standard RMC package but it is rather unique in its approach to solving an atomic or molecular structure.fullrmc's Engine sub-module is the main module that contains the definition of 'Engine' which is the main and only class used to launch an RMC calculation.
Engine reads only Protein Data Bank formatted atomic configuration files '.pdb' and handles other definitions and attributes.

