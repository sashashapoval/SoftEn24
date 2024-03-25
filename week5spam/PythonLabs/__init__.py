# Initializations for PythonLabs modules

# Classes that read project data need to know the path to the installed module

import os
import glob

datadir = os.path.join(os.path.dirname(__file__), "data") 

datafile = { }

for d in ['eliza', 'email', 'huffman', 'mars', 'spheres', 'text', 'tsp']:
    p = os.path.join(datadir, d)
    for fn in glob.glob(p + "/*"):
        df = os.path.basename(fn)
        datafile[df] = fn

