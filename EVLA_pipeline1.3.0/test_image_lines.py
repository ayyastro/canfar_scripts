
'''
Create test images of the central channels using the calibrator.
'''

pipepath = '/lustre/aoc/observers/nm-7669/canfar_scripts/EVLA_pipeline1.3.0/'

execfile(pipepath+"EVLA_pipe_restore.py")

# Based on C config beam
myimsize = 2048
mycell = "3arcsec"

for i in spws:
    for cal_field in calibrator_field_list:
        print("Imaging calibrator in SPW "+str(i))

        try:
            imname = "calibrator_field" + str(cal_field) + "_spw" + str(i) + ".image"

            default('clean')
            vis = 'calibrators.ms'
            imagename = imname
            outlierfile = ''
            field = str(cal_field)
            spw = str(i)
            selectdata = False
            mode = 'channel'
            nchan = 1
            width = 1
            start = 0
            reffreq = ''
            gridmode = ''
            niter = 0
            threshold = '0.0mJy'
            imagermode = ''
            imsize = [myimsize, myimsize]
            cell = [mycell, mycell]
            phasecenter = ''
            restfreq = ''
            stokes = 'I'
            weighting = 'uniform'
            uvtaper = False
            modelimage = ''
            restoringbeam = ['']
            pbcor = False
            minpb = 0.2
            calready = False
            allowchunk = False
            async = False
            clean()

        except Exception, e:
            logprint("Problem with " + str(cal_field) + " " + str(i) + " " + imname)
            print e
