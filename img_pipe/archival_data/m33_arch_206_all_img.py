
'''
Imaging B and C configs together. Also using Arecibo data as the input model.
Optional feathering of Arecibo and combine VLA image together.
'''

import os

from tasks import *
from taskinit import *
import casac


# vis_path = 'VLA/archival/'
vis = "M33_b_c.ms"
out_root = 'M33_206_b_c'


# mod_path = 'Arecibo/'
model = 'M33_model.image'
mask = 'M33_mask.image'

combine_configs = False
do_cvel = False
do_dirtyimage = False
do_clean_1chan = False
do_clean = True
do_export = True

if combine_configs:
    print("Combining the reduced B and C configuration data.")

    concat(vis=["../b_config/M33_bconfig_all.split.contsub",
                "../c_config/M33.split.contsub"],
           concatvis=vis,
           timesort=True, freqtol='10MHz')

if do_cvel:

    os.system('rm -rf '+out_root+'.cvel')
    cvel(vis=vis, outputvis=out_root+'.cvel', mode='channel',
         nchan=-1, start=0, width=1, restfreq='1420.40575177MHz',
         outframe='LSRK', phasecenter='J2000 01h33m50.904 +30d39m35.79')

    vis = out_root+'.cvel'

if do_dirtyimage:
    # First creates a dirty cube to examine

    print "Making dirty cube."

    os.system('rm -rf '+out_root+'.dirty*')

    clean(vis=vis, imagename=out_root+'.dirty_mask_model', restfreq='1420.40575177MHz',
          mode='channel', width=1, nchan=205, start=10,
          cell='1.5arcsec', multiscale=[0, 3, 9, 27, 200],
          threshold='2.0mJy/beam', imagermode='mosaic',
          imsize=[4096, 4096], weighting='natural', robust=0.0, niter=0,
          pbcor=True, interpolation='linear', usescratch=True,
          phasecenter='J2000 01h33m50.904 +30d39m35.79', veltype='radio',
          outframe='LSRK', modelimage=model, mask=mask)

if do_clean_1chan:

    # os.system('rm -rf '+out_root+'.chan*')

    For multiscale, 1 pixel = 3 arcsec in C, 1 pix = 1.5 arcsec in B.

    model_110 = "../../../Arecibo/M33_model_channel_110.image"
    mask_110 = "../../../Arecibo/M33_newmask_channel_110.image"

    clean(vis=vis, imagename=out_root+'.chan_110', field='M33*',
          restfreq='1420.40575177MHz', mode='channel', nterms=1,
          width=1, nchan=1, start=110, cell='1.5arcsec',
          imsize=[4096, 4096], weighting='natural', niter=50000,
          threshold='2.2mJy/beam', imagermode='mosaic', gain=0.5,
          multiscale=[0, 8, 20], interactive=False,
          pbcor=True, interpolation='linear', usescratch=True,
          phasecenter='J2000 01h33m50.904 +30d39m35.79', veltype='radio',
          outframe='LSRK', modelimage=model_110, mask=mask_110)

    model_65 = "../../../Arecibo/M33_model_channel_65.image"
    mask_65 = "../../../Arecibo/M33_newmask_channel_65.image"

    clean(vis=vis, imagename=out_root+'.chan_65', field='M33*',
          restfreq='1420.40575177MHz', mode='channel', nterms=1,
          width=1, nchan=1, start=65, cell='1.5arcsec',
          imsize=[4096, 4096], weighting='natural', niter=50000,
          threshold='2.2mJy/beam', imagermode='mosaic', gain=0.5,
          multiscale=[0, 8, 20], interactive=False,
          pbcor=True, interpolation='linear', usescratch=True,
          phasecenter='J2000 01h33m50.904 +30d39m35.79', veltype='radio',
          outframe='LSRK', modelimage=model_65, mask=mask_65)

if do_clean:

    print 'Making cleaned cube.'

    os.system('rm -rf '+out_root+'.clean')

    parallel = False

    if not parallel:
        clean(vis=vis, imagename=out_root+'.clean', field='M33*',
              restfreq='1420.40575177MHz',
              mode='channel', width=1, nchan=205, start=10,
              cell='1.5arcsec', multiscale=[0, 8, 20],
              threshold='2.2mJy/beam', imagermode='mosaic', gain=0.5,
              imsize=[4096, 4096], weighting='natural', robust=0.0, niter=50000,
              pbcor=True, interpolation='linear', usescratch=True,
              phasecenter='J2000 01h33m50.904 +30d39m35.79', veltype='radio',
              outframe='LSRK', modelimage=model, mask=mask)
    else:
        pclean(vis=vis, imagename=out_root+'.clean', field='M33*',
               restfreq='1420.40575177MHz',
               mode='channel', width=1, nchan=205, start=10,
               cell='1.5arcsec', alg='multiscale', scales=[0, 8, 20],
               threshold='2.2mJy/beam', ftmachine='mosaic', gain=0.5,
               imsize=[4096, 4096], weighting='natural', robust=0.0, niter=50000,
               pbcor=True, interpolation='linear', usescratch=True,
               phasecenter='J2000 01h33m50.904 +30d39m35.79', veltype='radio',
               outframe='LSRK', modelimage=model, mask=mask,
               clusterdef='')

if do_export:

    print "Exporting fits files."

    # Clean cube
    exportfits(imagename=out_root+'.clean.image',
               fitsimage=out_root+'.fits', overwrite=True,
               velocity=True, dropstokes=True)

    # Residual cube
    exportfits(imagename=out_root+'.clean.residual',
               fitsimage=out_root+'_resid.fits', overwrite=True,
               velocity=True, dropstokes=True)

    # Export the primary beam image for the cleaned cube
    exportfits(imagename=out_root+'.clean.flux',
               fitsimage=out_root+'_flux.fits', overwrite=True,
               velocity=True, dropstokes=True)
