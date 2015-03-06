import os
import numpy as np
import sys

try:
    SDM_name = str(sys.argv[5])
except IndexError:
    # The prefix to use for all output files
    SDM_name = '14B-088.sb30023144.eb30070731.57002.919034293984'

# Set up some useful variables (these will be altered later on)
msfile = SDM_name + '.ms'
hisplitms = SDM_name + '.hi.ms'
splitms = SDM_name + '.hi.src.split.ms'

pathname = os.environ.get('CASAPATH').split()[0]
pipepath = '/home/ekoch/pipe_scripts/'

source = 'M33'

# VOS stuff
vos_dir = '../vos/'
vos_proc = './'

# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%
# Find the 21cm spw and check if the obs
# is single pointing or mosaic
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%

print "Find HI spw..."

# But first find the spw corresponding to it
tb.open(vos_dir+msfile+'/SPECTRAL_WINDOW')
freqs = tb.getcol('REF_FREQUENCY')
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(0, len(freqs))


# Select the 21cm

sel = np.where((freqs > 1.40*10**9) & (freqs < 1.43*10**9))
hispw = str(spws[sel[0][0]])
freq = freqs[sel[0][0]]
nchan = nchans[sel[0][0]]

print "Selected spw "+str(hispw)
print "with frequency "+str(freq)
print "and "+str(nchan)+" channels"
print "Starting split the HI line"

# Mosaic or single pointing?

tb.open(vos_dir+msfile+'/FIELD')
names = tb.getcol('NAME')
tb.close()

moscount = 0

for name in names:
    chsrc = name.find(source)

    if chsrc != -1:
        moscount = moscount+1

if moscount > 1:
    imagermode = "mosaic"
else:
    imagermode = "csclean"


# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# Split the corrected source data from the rest
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%


print "Starting source split..."

#os.system('md5sum $(find '+vos_dir+hisplitms+') > '+vos_proc+hisplitms+'.md5')

# os.system('rm -rf '+vos_proc+splitms)

default('split')
vis = vos_dir+hisplitms
outputvis = vos_proc+splitms
field = source
spw = hispw
datacolumn = 'corrected'
keepflags = False

print vis
print outputvis
print field
print spw

split()

print "Created splitted-source .ms "+splitms
