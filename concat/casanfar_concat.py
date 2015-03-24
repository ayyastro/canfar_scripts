import os
import numpy as np
import sys

try:
    conc_name = str(sys.argv[4])
    SDM_names = str(sys.argv[5:])
except IndexError as e:
    # The prefix to use for all output files
    raise e("No MS sets specified. Or the casapy preamble has more args"
            "than expected. Script expects 4 cmd line args before paths"
            "(including 'casapy').")

print("MS Files should contain the complete paths. Do not have trailing '/'."
      "Do not append '.ms'.")

# Set up some useful variables (these will be altered later on)
num_ms = len(SDM_names)
msfiles = [fil_name+".ms" for fil_name in SDM_names]
concatms = conc_name+".ms"

pathname = os.environ.get('CASAPATH').split()[0]
pipepath = '/home/ekoch/canfar_scripts/EVLA_pipeline1.3.0/'

source = 'M33*'

# VOS stuff
vos_dir = '../vos/'
vos_proc = './'

# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# Concatenate the corrected source data
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%


print "Starting source concatenating..."

os.system('rm -rf '+vos_proc+concatms)

default('concat')
vis = msfiles
concatvis = vos_proc+concatms
timesort = True
concat()

print "Created splitted-source .ms "+concatms
