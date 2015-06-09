
import sys
import os
import numpy as np
from datetime import datetime
import copy

'''
EVLA pipeline running for mixed setups.

Applies the first few steps of the pipeline up to basic flagging
(shadowing, zeros, ...). The continuum and line spws are then split
into their own directories. The full pipeline is then run on each. The lines
do not have rflag run on them.
'''

# Give the name of the ms. The folder containing the ms will be used for the
# splits
try:
    vis = sys.argv[1]
    path_to_pipeline = sys.argv[2]
except IndexError:
    vis = raw_input("MS File? : ")
    path_to_pipeline = raw_input("Path to pipeline? : ")

if vis[-1] == "/":
    vis = vis[:-1]

if not path_to_pipeline[-1] == "/":
    path_to_pipeline += "/"

# Chop off the .ms
SDM_name = vis[:-3]
SDM_name_orig = copy.copy(SDM_name)

# Set Hanning smoothing
myHanning = 'y'

# Figure out which are the lines and which are the continuum SPWs.

tb.open(vis + '/SPECTRAL_WINDOW')
bandwidths = tb.getcol('TOTAL_BANDWIDTH')
tb.close()

# Define a threshold between expected bandwidths
# Going with 10 MHz
thresh_bw = 1.0e7

spws = np.arange(0, len(bandwidths))

line_spws = [str(i) for i in spws[np.where(bandwidths < thresh_bw)]]
cont_spws = [str(i) for i in spws[np.where(bandwidths > thresh_bw)]]

print("Line SPWs: " + str(line_spws))
print("Coninuum SPWs: " + str(cont_spws))

print("Running initial pipeline.")

execfile(path_to_pipeline + "EVLA_pipeline_initial_mixed.py")

print("Splitting by SPW.")
print("Starting at: " + str(datetime.now()))
os.mkdir('speclines')

split(vis=vis, outputvis="speclines/"+SDM_name+".speclines.ms",
      spw=",".join(line_spws))

os.mkdir('continuum')

split(vis=vis, outputvis="continuum/"+SDM_name+".continuum.ms",
      spw=",".join(line_spws))

print("Ending at: " + str(datetime.now()))
print("Running full pipeline on the spectral lines.")
print("Starting at: " + str(datetime.now()))

os.chdir("speclines")

SDM_name = SDM_name+".speclines.ms"
myHanning = 'n'

execfile(path_to_pipeline + "EVLA_pipeline.py")

print("Ending at: " + str(datetime.now()))
print("Running full pipeline on the spectral lines.")
print("Starting at: " + str(datetime.now()))

os.chdir("continuum")

SDM_name = SDM_name+".continuum.ms"
myHanning = 'n'

execfile(path_to_pipeline + "EVLA_pipeline_continuum.py")

print("Ending at: " + str(datetime.now()))
print("All done!")
