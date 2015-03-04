import os
import numpy as np
from scipy.optimize import curve_fit


def gauss(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2 / (2. * sigma**2))


scriptmode = True

SDM_name = 'test'  # The prefix to use for all output files
# SDM_name = '13A-213.sb20685305.eb20706999.56398.113012800924'

# Set up some useful variables (these will be altered later on)
msfile = SDM_name + '.ms'
hisplitms = SDM_name + '.hi.ms'
splitms = SDM_name + '.hi.src.split.ms'
contsubms = SDM_name + '.hi.src.split.ms.contsub'
rawcleanms = SDM_name + '.hi.src.split.ms.contsub.rawcleanimg'
cleanms = SDM_name + '.hi.src.split.ms.contsub.cleanimg'

pathname = os.environ.get('CASAPATH').split()[0]
pipepath = '/home/dcolombo/pipe_scripts/'
# pipepath = '/home/dario/pipe_scripts/'

source = 'SextansA'

# VOS stuff
vos_dir = '../vos/'
vos_proc = './'
vos_link = '../vos_link/'

# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%
# Find the 21cm spw and check if the obs
# is single pointing or mosaic
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%

print "Find HI spw..."

# But first find the spw corresponding to it
tb.open(vos_dir + msfile + '/SPECTRAL_WINDOW')
freqs = tb.getcol('REF_FREQUENCY')
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(0, len(freqs))


# Select the 21cm

sel = np.where((freqs > 1.40 * 10**9) & (freqs < 1.43 * 10**9))
hispw = str(spws[sel[0][0]])
freq = freqs[sel[0][0]]
nchan = nchans[sel[0][0]]

print "Selected spw ", hispw, "with frequency ", freq, "and ", nchan, " channels"
print "Starting split the HI line"

# Mosaic or single pointing?

tb.open(vos_dir + msfile + '/FIELD')
names = tb.getcol('NAME')
tb.close()

moscount = 0

for name in names:
    chsrc = name.find(source)

    if chsrc != -1:
        moscount = moscount + 1

if moscount > 1:
    imagermode = "mosaic"
else:
    imagermode = "csclean"


# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# Split the corrected source data from the rest
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%


print "Starting source split..."

os.system('rm -rf ' + vos_proc + splitms)

default('split')
vis = vos_dir + hisplitms
outputvis = vos_proc + splitms
field = source
spw = ''
datacolumn = 'corrected'
keepflags = False
split()

print "Created splitted-source .ms " + splitms


# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# UV continum subtraction
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

# 1) Save a .txt file of the amplitude vs
# channels, plotms runs only to get the
# ASCII file

print "Estimating channels with signal..."

real_amps = []
imag_amps = []

default('visstat')
vis = vos_proc + splitms
field = '0'
datacolumn = 'data'
selectdata = True
useflags = False

for nc in range(nchan):

    spw = '0:' + str(nc)

    axis = 'real'
    pdata = visstat()
    real_amps.append(pdata['DATA']['mean'])

    axis = 'imag'
    pdata = visstat()
    imag_amps.append(pdata['DATA']['mean'])

real_amps = np.asarray(real_amps)
imag_amps = np.asarray(imag_amps)

amps = np.sqrt(real_amps**2 + imag_amps**2)
chans = np.arange(nchan) + 1


# Guessing parameters for fitting
A = max(amps)
mu = chans[amps.tolist().index(A)]

hm = chans[amps > A / 2]
sigma = float(hm[-1] - hm[0]) / 2.35

opar, _ = curve_fit(gauss, chans, amps, p0=[A, mu, sigma])

# Move away to 3.5sigma for the fit, in order to exclude the data
# from the fit

chan1 = int(mu - 3.5 * opar[2])
chan2 = int(mu + 3.5 * opar[2])

fitspws = str(chan1) + '~' + str(chan2)

print "Signal within channels " + fitspws


print "Starting contsub..."


# Run the routinne
os.system('rm -rf ' + vos_proc + contsubms)

default('uvcontsub')
vis = vos_proc + splitms
fitspw = '0:' + fitspws
excludechans = True
solint = 0.0
fitorder = 0
fitmode = 'subtract'
splitdata = True

uvcontsub()

print "Created continum subtracted image" + contsubms


# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# CLEANing
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

print "Starting CLEANing..."

os.system('rm -rf ' + vos_proc + rawcleanms + '*')

# First generate a 0-iterations
# image to estimate the noise level
# (threshold)

# Get max baseline and dish size
bline_max = au.getBaselineExtrema(vos_proc + splitms)[0]

tb.open(vos_proc + splitms + '/ANTENNA')
dishs = tb.getcol('DISH_DIAMETER')
dish_min = min(dishs)
tb.close()

# Find the beam
hi_lambda = 299792458.0 / (freq)
min_lambda = 299792458.0 / (min(freqs))
syn_beam = (hi_lambda / bline_max) * 180 / np.pi * 3600
prim_beam = (min_lambda / dish_min) * 180 / np.pi * 3600


# Setting CLEANing parameters
sel_cell = str(round(syn_beam / 5)) + 'arcsec'
sel_imsize = int(round(prim_beam / (syn_beam / 5)))

# Increase the sel_imsize of a couple of beam
# to be sure

dx = int(round(syn_beam / prim_beam * sel_imsize))
sel_imsize = sel_imsize + 1 * dx

# The image size should be a multiplier of
# 2, 3 and 5 to work well with clean so:

sel_imsize = sel_imsize - 1
pnum = 1 * sel_imsize

while pnum != 1:

    sel_imsize = sel_imsize + 1
    pnum = 1 * sel_imsize

    while pnum % 2 == 0:
        pnum = pnum / 2

    while pnum % 3 == 0:
        pnum = pnum / 3

    while pnum % 5 == 0:
        pnum = pnum / 5


print "Image size:", sel_imsize
print "Cell size:", sel_cell

# First generate a 0-iterations
# image to estimate the noise level
# (threshold)

default('clean')

vis = vos_proc + contsubms
imagename = vos_proc + rawcleanms
cell = [sel_cell, sel_cell]
imsize = [sel_imsize, sel_imsize]
imagermode = imagermode
mode = "channel"
nchan = 4
start = chan1 - 5
width = 1
field = '0'
spw = '0'
interactive = False
pbcor = False
minpb = 0.25
restfreq = '1.420405752GHz'
niter = 0

clean()


print "Estimating sigma..."

default('imstat')

imagename = vos_proc + rawcleanms + '.image'
chans = '0~3'
rawclean_stat = imstat()

rms = rawclean_stat['sigma'][0] * 1000
rms = round(rms)
rms = str(int(rms)) + 'mJy'


print "Sigma=", rms, ". Now the real CLEANing..."


# Now run the real cleaning
os.system('rm -rf ' + cleanms + '*')

default('clean')

vis = vos_proc + contsubms
imagename = vos_proc + cleanms
cell = [sel_cell, sel_cell]
imsize = [sel_imsize, sel_imsize]
imagermode = imagermode
mode = "channel"
start = chan1
nchan = chan2 - chan1
width = 1
field = ''
spw = ''
interactive = False
restfreq = '1.420405752GHz'
outframe = 'LSRK'
niter = 10000
threshold = rms
usescratch = True

clean()


# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# Moment maps 0,1,2
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

default("immoments")

imagename = vos_proc + cleanms + '.image'
moments = [0, 1, 2]
outfile = vos_proc + cleanms

immoments()

# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
# Convert everything to fits file
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

print "Exporting the image fits..."
default('exportfits')

imagename = vos_proc + cleanms + '.image'
fitsimage = vos_proc + source + '_21cm.fits'
velocity = True
optical = False
overwrite = True
dropstokes = True

exportfits()


print "Exporting moment maps..."
default('exportfits')

# Moment 0
imagename = vos_proc + cleanms + '.integrated'
fitsimage = vos_proc + source + '_21cm_mom0.fits'
velocity = True
optical = False
overwrite = True
dropstokes = True

exportfits()


default('exportfits')

# Moment 1
imagename = vos_proc + cleanms + '.weighted_coord'
fitsimage = vos_proc + source + '_21cm_mom1.fits'
velocity = True
optical = False
overwrite = True
dropstokes = True

exportfits()


default('exportfits')

# Moment 2
imagename = vos_proc + cleanms + '.weighted_dispersion_coord'
fitsimage = vos_proc + source + '_21cm_mom2.fits'
velocity = True
optical = False
overwrite = True
dropstokes = True

exportfits()
