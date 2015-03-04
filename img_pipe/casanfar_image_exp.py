import os
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt


def plotmosaic(vis='', sourceid='', figfile='', coord='relative', skipsource=-1,
               doplot=True, help=False, sciencespws=False, vm='', debug=False,
               intent='OBSERVE_TARGET#ON_SOURCE'):
    """
    Produce a plot of the pointings with the primary beam FWHM and field names.
    For further help and examples, see
    http://casaguides.nrao.edu/index.php?title=Plotmosaic
    Required parameters:
    vis: the measurement set

    Optional parameters:
    sourceid: int or string (name or ID)
    figfile: name of the png to produce
    coord: 'relative' or 'absolute'
    skipsource: source ID to avoid
    doplot: if False, then the central field ID is returned as an integer.
            if True, the a list of values is returned:
               [central field,  maxRA, minRA, minDec, maxDec]
       where the latter 4 values are in units of arcsec relative to the center.
    sciencespws: if True, then only use the science spws
    vm: a ValueMapping structure (obsolete, only for CASA < 4.1)
    debug: if True, print extra messages
    intent: determine the source IDs to use from this intent (if sourceid='')

    -- Todd Hunter
    """

    # open the ms table
    if (coord.find('abs') < 0 and coord.find('rel') < 0):
        print "Invalid option for coord, must be either 'rel'ative or 'abs'olute."
        return

    mytb = au.createCasaTool(tbtool)
    try:
        fieldTable = vis+'/FIELD'
        mytb.open(fieldTable)
    except:
        print "Could not open table = %s" % fieldTable
        return

    delayDir = mytb.getcol('DELAY_DIR')
    sourceID = mytb.getcol('SOURCE_ID')
    name = mytb.getcol('NAME')
    if (type(sourceid) == str):
        try:
            sourceid = int(sourceid)
        except:
            # Source was specified by name, so we
            # need to convert the name to an id.
            matches = np.where(name == sourceid)[0]
            srcs = np.unique(sourceID[matches])
            nsrcs = len(srcs)
            if nsrcs > 1:
                print "More than one source ID matches this name: ",sourceID
                print "Try again using one of these."
                return
            elif nsrcs == 0:
                if (sourceid != ''):
                    print "No sources match this name = %s" % sourceid
                    print "Available sources = ", np.unique(name)
                    return
                else:
                    if casadef.casa_version >= au.casaVersionWithMSMD:
                        print "No source specified, so using the intent %s." % (intent)
                    else:
                        print "No source specified, so using the first source."
                        sourceid = 0
                        return
            else:
                sourceid = srcs[0]

    #  sourcename = name[sourceid]  # original method, replaced by the line after the 'if' block
    fields = np.array(range(len(sourceID)))
    if (sourceid != ''):
        matches = np.where(sourceID == int(sourceid))[0]
        fields = fields[matches]
        matches = np.where(fields != skipsource)[0]
        fields = fields[matches]
        if (len(fields) < 1):
            print "No fields contain source ID = ", sourceid
            return
        print "Field IDs with matching source ID = ", fields
        sourcename = name[list(sourceID).index(sourceid)]  # protects against the case of non-consecutive source IDs
    else:
        mymsmd = au.createCasaTool(msmdtool)
        mymsmd.open(vis)
        # fields = mymsmd.fieldsforintent(intent)
        # if (len(fields) == 0):
        #     fields = mymsmd.fieldsforintent('*'+intent+'*')
        #     if (len(fields) == 0):
        #         print "No fields have intent = %s. Using first field instead." % (intent)
        #         fields = [0]
        sourcename = mymsmd.namesforfields(fields[0])[0]
        mymsmd.close()
        srcID = sourceID[list(name).index(sourcename)]
        print "Found %d fields for source ID=%d: %s: %s" % (len(fields), srcID, sourcename, str(fields))

    name = mytb.getcol('NAME')
    mytb.close()
    mytb.open(vis)
    antennasWithData = np.sort(np.unique(mytb.getcol('ANTENNA1')))
    mytb.close()
    try:
        antennaTable = vis+'/ANTENNA'
        mytb.open(antennaTable)
    except:
        print "Could not open table = %s" % antennaTable
        return

    dishDiameter = np.unique(mytb.getcol('DISH_DIAMETER')[antennasWithData])
    mytb.close()
    if (debug):
        print "dishDiameter = ", dishDiameter
    try:
        spwTable = vis+'/SPECTRAL_WINDOW'
        mytb.open(spwTable)
        num_chan = mytb.getcol('NUM_CHAN')
        refFreqs = mytb.getcol('REF_FREQUENCY')
        spwNames = mytb.getcol('NAME')
        bandNames = []
        for spwName in spwNames:
            bandNames.append(spwName.split('#')[0])
        bandNames = np.unique(bandNames)
        if (debug):
            print "bandNames = ", bandNames
        mytb.close()
    except:
        print "Could not open table = %s" % antennaTable
        print "Will not print primary beam circles"
        titleString = vis.split('/')[-1]
        dishDiameter = [0]
    [latitude, longitude, obs] = au.getObservatoryLatLong('EVLA')
    if debug:
        print "Got observatory longitude = %.3f deg" % (longitude)

    tsysOnlyFields = []
    if sciencespws:
        if casadef.casa_version >= casaVersionWithMSMD:
            mymsmd = createCasaTool(msmdtool)
            mymsmd.open(vis)
            spws = mymsmd.spwsforintent('OBSERVE_TARGET#ON_SOURCE')
            wvrspws = mymsmd.wvrspws()
            print "spws with observe_target = ", spws
            spws = [x for x in spws if x not in wvrspws]
            print "non-WVR = ", spws
            meanRefFreq = []
            for spw in spws:
                meanRefFreq.append(mymsmd.meanfreq(spw))
            meanRefFreq = np.mean(meanRefFreq)
            for f in fields:
                tsysOnly = True
                scans = mymsmd.scansforfield(f)
                for sc in scans:
                    scanIntents = mymsmd.intentsforscan(sc)
                    if ('CALIBRATE_ATMOSPHERE#ON_SOURCE' not in scanIntents):
                        tsysOnly = False
                if tsysOnly:
                    tsysOnlyFields.append(f)
            print "fields with Tsys only = ", tsysOnlyFields
            mymsmd.close()
        else:
            if vm == '':
                vm = ValueMapping(vis)
            spws = vm.getSpwsForIntent('OBSERVE_TARGET#ON_SOURCE')
            for f in fields:
                tsysOnly = True
                scans = vm.getScansForField(f)
                for sc in scans:
                    scanIntents = vm.getIntentsForScan(sc)
                    if ('CALIBRATE_ATMOSPHERE#ON_SOURCE' not in scanIntents):
                        tsysOnly = False
                if tsysOnly:
                    tsysOnlyFields.append(f)
            print "spws with observe_target = ", spws
            print "fields with Tsys only = ", tsysOnlyFields
            matchedNames = np.array(bandNames)[spws]
            matchedRefFreqs = np.array(refFreqs)[spws]
            matches = np.where(matchedNames != 'WVR')
            print "non-WVR = ", matchedNames[matches]
            meanRefFreq = np.mean(matchedRefFreqs[matches])
    else:
        if 3840 in num_chan:
            matches = np.where(num_chan == 3840)[0]
        else:
            # this kills the WVR and channel averaged data
            matches = np.where(num_chan > 4)[0]
        meanRefFreq = np.mean(refFreqs[matches])
        # myband = freqToBand(meanRefFreq)[0]
        # print "Mean frequency = %f GHz (band = %d)" % (meanRefFreq*1e-9, myband)
        # # If mean freq is not within one of the observed bands, then recalculate
        # if ('ALMA_RB_%02d'%(myband) not in bandNames and len(bandNames) > 1): # old data do not have band names in spw names
        #     print "Mean frequency is not in any observed band. Recalculating over higher frequencies."
        #     newFreqs = refFreqs[matches]
        #     newmatches = np.where(newFreqs > meanRefFreq)[0]
        #     meanRefFreq = np.mean(newFreqs[newmatches])
        #     print "Mean frequency = %f GHz" % (meanRefFreq*1e-9)
    lambdaMeters = au.c_mks / meanRefFreq
    ra = delayDir[0, :][0]*12 / np.pi
    dec = delayDir[1, :][0]*180 / np.pi
    ra *= 15
    raAverageDegrees = np.mean(ra[fields])
    decAverageDegrees = np.mean(dec[fields])
    cosdec = 1.0 / np.cos(decAverageDegrees*np.pi/180)

    # Here we scale by cos(dec) to make then pointing pattern in angle on sky
    raRelativeArcsec = 3600*(ra - raAverageDegrees)*cos(decAverageDegrees*np.pi/180.)
    decRelativeArcsec = 3600*(dec - decAverageDegrees)

    markersize = 4
    print "Found %d pointings in this ms" % (au.shape(ra)[0])
    [centralField, smallestSeparation] = \
        au.findNearestField(ra[fields], dec[fields],
                            raAverageDegrees, decAverageDegrees)
    # This next step is crucial, as it converts from the field number
    # determined from a subset list back to the full list.
    centralField = fields[centralField]

    print "Field %d is closest to the center of the area covered (%.1f arcsec away)." \
        % (centralField, smallestSeparation*3600)
    if not doplot:
        return centralField

    plt.clf()
    maxradius = 0
    desc = plt.subplot(111)
    if coord.find('abs' >= 0):
        raunit = 'deg'  # nothing else is supported (yet)
        desc = plt.subplot(111, aspect=cosdec)
        # SHOW ABSOLUTE COORDINATES
        plt.plot(ra[fields], dec[fields], "k+", markersize=markersize)
        for j in dishDiameter:
            for i in range(len(ra)):
                if i not in fields:
                    continue
                if not j > 0:
                    continue

                arcsec = \
                    0.5*primaryBeamArcsec(wavelength=lambdaMeters*1000,
                                          diameter=j,
                                          showEquation=False)
                radius = arcsec/3600.0
                if radius > maxradius:
                    maxradius = radius
                if i in tsysOnlyFields:
                    myedgecolor = 'r'
                else:
                    myedgecolor = 'b'
                    if len(dishDiameter) > 1 and j < 12:
                        # Draw ACA in black
                        myedgecolor = 'k'
                print "Plotting ellipse with radius = ", radius
                cir = matplotlib.patches.Ellipse((ra[i], dec[i]),
                                                 width=2*radius*cosdec,
                                                 height=2*radius,
                                                 facecolor='none',
                                                 edgecolor=myedgecolor,
                                                 linestyle='dotted')
                plt.gca().add_patch(cir)
                cir = plt.Circle((ra[i], dec[i]), radius=radius,
                                 facecolor='none', edgecolor='b',
                                 linestyle='dotted')

        titleString = \
            vis.split('/')[-1]+', %s, average freq. = %.1f GHz, beam = %.1f"'\
            % (sourcename, meanRefFreq*1e-9, 2*arcsec)
        plt.title(titleString, size=10)

        resizeFonts(desc, 10)
        if raunit.find('deg') >= 0:
            plt.xlabel('Right Ascension (deg)')
        else:
            plt.xlabel('Right Ascension (hour)')
        plt.ylabel('Declination (deg)')

        raRange = np.max(ra[fields])-np.min(ra[fields])
        decRange = np.max(dec[fields])-np.min(dec[fields])
        x0 = np.max(ra[fields]) + 1.2*maxradius*cosdec
        x1 = np.min(ra[fields]) - 1.2*maxradius*cosdec
        y1 = np.max(dec[fields]) + 1.2*maxradius
        y0 = np.min(dec[fields]) - 1.2*maxradius
        plt.xlim([x0, x1])
        plt.ylim([y0, y1])
        for i in range(len(ra)):
            if i not in fields:
                continue
            plt.text(ra[i]-0.02*raRange, dec[i]+0.02*decRange, str(i),
                     fontsize=12, color='k')
    elif coord.find('rel') >= 0:
        # SHOW RELATIVE COORDINATES
        plt.plot(raRelativeArcsec[fields], decRelativeArcsec[fields], 'k+',
                 markersize=markersize)
        for j in dishDiameter:
            for i in range(len(ra)):
                if i not in fields:
                    continue
                if not j > 0:
                    continue

                arcsec = \
                    0.5*au.primaryBeamArcsec(wavelength=lambdaMeters*1000,
                                             diameter=j, showEquation=False)
                radius = arcsec
                if radius > maxradius:
                    maxradius = radius
                if i in tsysOnlyFields:
                    myedgecolor = 'r'
                else:
                    myedgecolor = 'b'
                    if len(dishDiameter) > 1 and j < 12:
                        # Draw ACA in black
                        myedgecolor = 'k'
                print "Plotting circle with radius = ", radius
                cir = plt.Circle((raRelativeArcsec[i], decRelativeArcsec[i]),
                                 radius=radius, facecolor='none',
                                 edgecolor=myedgecolor, linestyle='dotted')
                plt.gca().add_patch(cir)

        titleString = \
            vis.split('/')[-1]+', %s, average freq. = %.1f GHz, beam = %.1f"'\
            % (sourcename, meanRefFreq*1e-9, 2*arcsec)
        plt.title(titleString, size=10)

        au.resizeFonts(desc, 10)

        raString = qa.formxxx('%fdeg' % (raAverageDegrees), format='hms',
                              prec=2)
        decString = qa.formxxx('%fdeg' % (decAverageDegrees), format='dms',
                               prec=0).replace('.', ':', 2)

        plt.xlabel('Right ascension offset (arcsec) from %s' % (raString))
        plt.ylabel('Declination offset (arcsec) from %s' % (decString))

        raRange = np.max(raRelativeArcsec[fields]) - \
            np.min(raRelativeArcsec[fields])
        decRange = np.max(decRelativeArcsec[fields]) - \
            np.min(decRelativeArcsec[fields])
        for i in range(len(ra)):
            if i not in fields:
                continue

            if i not in tsysOnlyFields:

                plt.text(0.05, 0.93,
                         'Tsys-only fields: %s' % (str(tsysOnlyFields)),
                         transform=desc.transAxes, color='r')
                mycolor = 'r'
            else:
                mycolor = 'k'

            plt.text(raRelativeArcsec[i]-0.02*raRange,
                     decRelativeArcsec[i]+0.02*decRange,
                     str(i), fontsize=12, color=mycolor)

        x0 = np.max(raRelativeArcsec[fields]) + 1.2*maxradius  # 0.25*raRange
        x1 = np.min(raRelativeArcsec[fields]) - 1.2*maxradius  # - 0.25*raRange
        y1 = np.max(decRelativeArcsec[fields]) + 1.2*maxradius  # 0.25*decRange
        y0 = np.min(decRelativeArcsec[fields]) - 1.2*maxradius  # 0.25*decRange

        mosaicInfo = []
        mosaicInfo.append(centralField)
        mosaicInfo.append(np.max(raRelativeArcsec[fields]) + 2*maxradius)
        mosaicInfo.append(np.min(raRelativeArcsec[fields]) - 2*maxradius)
        mosaicInfo.append(np.max(decRelativeArcsec[fields]) + 2*maxradius)
        mosaicInfo.append(np.min(decRelativeArcsec[fields]) - 2*maxradius)

        plt.xlim(x0, x1)
        plt.ylim(y0, y1)
        plt.axis('equal')
    else:
        print "Invalid option for coord, must be either 'rel'ative or 'abs'olute."
        return

    yFormatter = au.ScalarFormatter(useOffset=False)
    desc.yaxis.set_major_formatter(yFormatter)
    desc.xaxis.set_major_formatter(yFormatter)
    desc.xaxis.grid(True, which='major')
    desc.yaxis.grid(True, which='major')
    if len(dishDiameter) > 1:
        plt.text(0.04, 0.03, '12m', color='b', transform=desc.transAxes)
        plt.text(0.04, 0.08, '7m', color='k', transform=desc.transAxes)
    plt.draw()
    autoFigureName = "%s.pointings.%s.png" % (vis, coord)

    if figfile:
        try:
            plt.savefig(autoFigureName)
            print "Wrote file = %s" % (autoFigureName)
        except:
            print "WARNING:  Could not save plot file.  Do you have write permission here?"
    elif len(figfile) > 0:
        try:
            plt.savefig(figfile)
            print "Wrote file = %s" % (figfile)
        except:
            print "WARNING:  Could not save plot file.  Do you have write permission here?"
    else:
        print "To save a plot, re-run with either:"
        print "  plotmosaic('%s',figfile=True) to produce the automatic name=%s" % (vis, autoFigureName)
        print "  plotmosaic('%s',figfile='myname.png')" % (vis)

    if coord.find('rel') >= 0:
        return mosaicInfo
    else:
        return


def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


scriptmode = True

#SDM_name = '14B-088.sb29701604.eb29882607.56952.08797296297.ms' # The prefix to use for all output files
#SDM_name = '13A-213.sb20685305.eb20706999.56398.113012800924'

SDM_name = '14B-088.sb29812125.eb29987192.56975.23496244213.ms'

# Set up some useful variables (these will be altered later on)
msfile = SDM_name  # + '.ms'

pathname = os.environ.get('CASAPATH').split()[0]
pipepath = '/home/dcolombo/pipe_scripts/'
#pipepath = '/home/dario/pipe_scripts/'

"""
HI            ; 1.420405752GHz; 9
OH1612  ; 1.612231GHz      ; 12
OH1665  ; 1.6654018GHz    ; 14
OH1667  ; 1.667359GHz      ; 15
OH1720  ; 1.72053GHz        ; 16
H(172)alp; 1.28117GHz        ; 8
H(152)alp; 1.85425GHz        ; 18
H(153)alp; 1.81825GHz        ; 17
H(166)alp; 1.42473GHz        ; 10
H(158)alp; 1.65154GHz        ; 13
H(164)alp; 1.47734GHz        ; 11
"""

source = 'M33'
restfreqs = ['1.420405752GHz', '1.612231GHz', '1.6654018GHz',
             '1.667359GHz', '1.72053GHz', '1.28117GHz',
             '1.85425GHz', '1.81825GHz', '1.42473GHz',
             '1.65154GHz', '1.47734GHz']

#sspws = [9,12,14,15,16,8,18,17,10,13,11]
sspws = [9]

# VOS stuff
# vos_dir = '/staging/tmp/vos/'
# vos_proc = '/staging/tmp/proc/'
# vos_cache = '/staging/tmp/vos_cache/'

# vos_dir = '/Volumes/Zeruel_data/M33/'
# vos_proc = '/Volumes/Zeruel_data/M33/'

vos_dir = '../vos/'
vos_proc = './'
vos_cache = '../vos_cache/'

# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%
# Find the 21cm spw and check if the obs
# is single pointing or mosaic
# %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%%&%&%&%&%&%&%%&%

# But first find the spw corresponding to it
tb.open(vos_dir+msfile+'/SPECTRAL_WINDOW')
freqs = tb.getcol('REF_FREQUENCY')
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(0, len(freqs))


# Mosaic or single pointing?

tb.open(vos_dir+msfile+'/FIELD')
names = tb.getcol('NAME')
tb.close()

moscount = 0
srcfields = []

for name in names:
    chsrc = name.find(source)

    if chsrc != -1:
        moscount = moscount+1
        srcfields.append(names.tolist().index(name))

if moscount > 1:

    simagermode = "mosaic"

    ssrcfield = ''
    ssplitfield = ''
    for j in range(len(srcfields)-1):

        ssrcfield = ssrcfield + str(srcfields[j])+','
        ssplitfield = ssplitfield + str(j)+','

    ssrcfield = ssrcfield + str(srcfields[-1])
    ssplitfield = ssplitfield + str(len(srcfields))

else:

    simagermode = "csclean"
    ssrcfield = str(srcfields[0])
    ssplitfield = '0'


for sspw in sspws:

    # Select the spw

    freq = freqs[sspw]
    nchan = nchans[sspw]

    print "Selected spw ", sspw, "with frequency ", freq, "and ", nchan, " channels"
    print "Starting split the selected spw"


    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    # Split the corrected source data from the rest
    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%


    print "Starting source split..."

    splitms = SDM_name+'.spw'+str(sspw)+'.ms'
    os.system('rm -rf '+vos_proc+splitms)

    default('split')
    vis = vos_dir+msfile
    outputvis = vos_proc+splitms
    field = ssrcfield
    spw = str(sspw)
    datacolumn = 'corrected'
    keepflags = False
    split()

    print "Created splitted-source .ms "+splitms


    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    # UV continum subtraction
    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

    # 1) Save a .txt file of the amplitude vs
    # channels, plotms runs only to get the
    # ASCII file

    print "Estimating channels with signal..."

    chan1s = []
    chan2s = []

    sfields = range(len(srcfields))

    for sfield in sfields:

        print "Check field", sfield

        real_amps = []
        imag_amps = []

        default('visstat')
        vis = vos_proc+splitms
        field = str(sfield)
        datacolumn = 'data'
        selectdata = True
        useflags = False

        for nc in range(nchan):

            spw = '0:'+str(nc)

            axis = 'real'
            pdata = visstat()
            real_amps.append(pdata['DATA']['mean'])

            axis = 'imag'
            pdata = visstat()
            imag_amps.append(pdata['DATA']['mean'])

        real_amps = np.asarray(real_amps)
        imag_amps = np.asarray(imag_amps)

        amps = np.sqrt(real_amps**2+imag_amps**2)
        chans = np.arange(nchan)+1

        # Guessing parameters for fitting
        A = max(amps)
        mu = chans[amps.tolist().index(A)]

        hm = chans[amps > A/2]
        sigma = float(hm[-1]-hm[0])/2.35

        opar, _ = curve_fit(gauss, chans, amps, p0=[A, mu, sigma])

        # Move away to 3.5 sigma for the fit, in order to exclude the data
        # from the fit

        chan1 = int(mu - 3.5*opar[2])
        chan2 = int(mu + 3.5*opar[2])

        chan1s.append(chan1)
        chan2s.append(chan2)

    chan1 = min(chan1s)
    chan2 = max(chan2s)

    fitspws = str(chan1)+'~'+str(chan2)

    print "Signal within channels "+fitspws

    print "Starting contsub..."




    # Run the routine
    contsubms = splitms+'.contsub'
    os.system('rm -rf '+vos_proc+contsubms)

    default('uvcontsub')
    vis = vos_proc+splitms
    fitspw = '0:'+fitspws
    excludechans = True
    solint = 0.0
    fitorder = 0
    fitmode = 'subtract'
    splitdata = True

    uvcontsub()

    print "Created continum subtracted image"+contsubms


    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    # CLEANing
    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

    print "Starting CLEANing..."
    rawcleanms = contsubms+'.rawcleanimg'
    os.system('rm -rf '+vos_proc+rawcleanms+'*')

    tb.open(vos_proc+splitms+'/ANTENNA')
    dishs = tb.getcol('DISH_DIAMETER')
    dish_min = min(dishs)
    tb.close()

    # Get max baseline and dish size
    bline_max = au.getBaselineExtrema(vos_proc+splitms)[0]

    # Find the beam
    sel_lambda = 299792458.0/(freq)
    syn_beam = (sel_lambda/bline_max)*180/np.pi*3600

    # Setting CLEANing parameters
    sel_cell = str(round(syn_beam/5))+'arcsec'

    if simagermode is 'csclean':

        min_lambda = 299792458.0/(min(freqs))
        prim_beam = (min_lambda/dish_min)*180/np.pi*3600

        # Setting CLEANing parameters
        sel_imsize = int(round(prim_beam/(syn_beam/5)))

        # Increase the sel_imsize of a couple of beam
        # to be sure

        dx = int(round(syn_beam/prim_beam*sel_imsize))
        sel_imsize = sel_imsize+1*dx

    else:

        mos_sizes = plotmosaic(vis=vos_proc+contsubms, coord='rel')
        mos_width = max([np.abs(mos_sizes[1]-mos_sizes[2]),
                         np.abs(mos_sizes[3]-mos_sizes[4])])

        sel_imsize = int(round(mos_width/(syn_beam/5)))

    # The image size should be a multiplier of
    # 2, 3 and 5 to work well with clean so:

    sel_imsize = sel_imsize-1
    pnum = 1*sel_imsize

    while pnum != 1:

        sel_imsize = sel_imsize+1
        pnum = 1*sel_imsize

        while pnum % 2 == 0:
            pnum = pnum/2

        while pnum % 3 == 0:
            pnum = pnum/3

        while pnum % 5 == 0:
            pnum = pnum/5

    print "Image size:", sel_imsize
    print "Cell size:", sel_cell

    # First generate a 0-iterations
    # image to estimate the noise level
    # (threshold)

    default('clean')

    vis = vos_proc+contsubms
    imagename = vos_proc+rawcleanms
    cell = [sel_cell, sel_cell]
    imsize = [sel_imsize, sel_imsize]
    imagermode = simagermode
    mask = None
    weighting = 'briggs'
    robust = 0.0
    mode = "channel"
    nchan = 4
    start = chan1-5
    width = 1
    field = source+'*'
    spw = ''
    interactive = False
    interpolation = 'linear'
    outframe = 'LSRK'
    pbcor = False
    minpb = 0.25
    restfreq = restfreqs[spws.index(sspw)]
    niter = 0
    clean()

    print "Estimating sigma..."

    default('imstat')

    imagename = vos_proc+rawcleanms+'.image'
    chans = '0~3'
    rawclean_stat = imstat()

    rms = rawclean_stat['sigma'][0]*1000
    rms = round(rms)
    rms = str(int(rms))+'mJy'

    print "Sigma=",rms, ". Now the real CLEANing..."

    # Now run the real cleaning
    cleanms = contsubms+'.cleanimg'
    os.system('rm -rf '+cleanms+'*')

    default('clean')

    vis = vos_proc+contsubms
    imagename = vos_proc+cleanms
    cell = [sel_cell, sel_cell]
    imsize = [sel_imsize, sel_imsize]
    imagermode = imagermode
    mode = "channel"
    start = chan1
    nchan = chan2-chan1
    width = 1
    field = source+'*'
    spw = ''
    interactive = False
    restfreq = restfreqs[spws.index(sspw)]
    outframe = 'LSRK'
    niter = 10000
    threshold = rms
    usescratch = True
    clean()

    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    # Moment maps 0,1,2
    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

    default("immoments")

    imagename = vos_proc+cleanms+'.image'
    moments = [0, 1, 2]
    outfile = vos_proc+cleanms
    immoments()

    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%
    # Convert everything to fits file
    # %&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%&%

    print "Exporting the image fits..."
    default('exportfits')

    imagename = vos_proc+cleanms+'.image'
    fitsimage = vos_proc+source+'_spw'+str(sspw)+'.fits'
    velocity = True
    optical = False
    overwrite = True
    dropstokes = True
    exportfits()


    print "Exporting moment maps..."
    default('exportfits')

    # Moment 0
    imagename = vos_proc+cleanms+'.integrated'
    fitsimage = vos_proc+source+'_spw'+str(sspw)+'_mom0.fits'
    velocity = True
    optical = False
    overwrite = True
    dropstokes = True
    exportfits()

    default('exportfits')

    # Moment 1
    imagename = vos_proc+cleanms+'.weighted_coord'
    fitsimage = vos_proc+source+'_spw'+str(sspw)+'_mom1.fits'
    velocity = True
    optical = False
    overwrite = True
    dropstokes = True
    exportfits()

    default('exportfits')

    # Moment 2
    imagename = vos_proc+cleanms+'.weighted_dispersion_coord'
    fitsimage = vos_proc+source+'_spw'+str(sspw)+'_mom2.fits'
    velocity = True
    optical = False
    overwrite = True
    dropstokes = True
    exportfits()


