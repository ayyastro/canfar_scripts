
'''
Plot UVdist per field per SPW
Plot BP amp and phase per antenna per SPW

Requires that the pipeline namespace be populated.
'''

import os


# Repopulate namespace
execfile("EVLA_pipeline1.3.0/EVLA_pipe_restore.py")

# UV plots per SPW
for ii in field_ids:
    for jj in field_spws[ii]:
        print ii, jj
        default('plotms')
        vis = ms_active
        xaxis = 'uvwave'
        yaxis = 'amp'
        ydatacolumn = 'corrected'
        selectdata = True
        field = str(field_ids[ii])
        spw = str(field_spws[jj])
        correlation = corrstring
        averagedata = True
        avgchannel = str(max(channels))
        avgtime = '1e8s'
        avgscan = False
        transform = False
        extendflag = False
        iteraxis = ''
        # coloraxis = 'spw'
        plotrange = []
        title = 'Field ' + field + ', ' + field_names[ii] + " SPW " + spw
        xlabel = ''
        ylabel = ''
        showmajorgrid = False
        showminorgrid = False
        plotfile = 'field' + field + '_amp_uvdist.png'
        overwrite = True
        showgui = False
        async = False
        plotms()

# Final BP plots per SPW

nplots = int(numSpws / 3)

if ((numSpws % 3) > 0):
    nplots = nplots + 1

tb.open('finalBPcal.b')
dataVarCol = tb.getvarcol('CPARAM')
flagVarCol = tb.getvarcol('FLAG')
tb.close()

rowlist = dataVarCol.keys()
nrows = len(rowlist)
maxmaxamp = 0.0
maxmaxphase = 0.0
for rrow in rowlist:
    dataArr = dataVarCol[rrow]
    flagArr = flagVarCol[rrow]
    amps = np.abs(dataArr)
    phases = np.arctan2(np.imag(dataArr), np.real(dataArr))
    good = np.logical_not(flagArr)
    tmparr = amps[good]
    if (len(tmparr) > 0):
        maxamp = np.max(amps[good])
        if (maxamp > maxmaxamp):
            maxmaxamp = maxamp
    tmparr = np.abs(phases[good])
    if (len(tmparr) > 0):
        maxphase = np.max(np.abs(phases[good])) * 180. / pi
        if (maxphase > maxmaxphase):
            maxmaxphase = maxphase
ampplotmax = maxmaxamp
phaseplotmax = maxmaxphase

for ii in range(nplots):
    filename = 'finalBPcal_amp' + str(ii) + '.png'
    syscommand = 'rm -rf ' + filename
    os.system(syscommand)

    spwPlot = str(ii * 3) + '~' + str(ii * 3 + 2)

    default('plotcal')
    caltable = 'finalBPcal.b'
    xaxis = 'freq'
    yaxis = 'amp'
    poln = ''
    field = ''
    antenna = ''
    spw = spwPlot
    timerange = ''
    subplot = 311
    overplot = False
    clearpanel = 'Auto'
    iteration = 'antenna'
    plotrange = [0, 0, 0, ampplotmax]
    showflags = False
    plotsymbol = 'o'
    plotcolor = 'blue'
    markersize = 5.0
    fontsize = 10.0
    showgui = False
    figfile = filename
    async = False
    plotcal()

for ii in range(nplots):
    filename = 'finalBPcal_phase' + str(ii) + '.png'
    syscommand = 'rm -rf ' + filename
    os.system(syscommand)

    spwPlot = str(ii * 3) + '~' + str(ii * 3 + 2)

    default('plotcal')
    caltable = 'finalBPcal.b'
    xaxis = 'freq'
    yaxis = 'phase'
    poln = ''
    field = ''
    antenna = ''
    spw = spwPlot
    timerange = ''
    subplot = 311
    overplot = False
    clearpanel = 'Auto'
    iteration = 'antenna'
    plotrange = [0, 0, -phaseplotmax, phaseplotmax]
    showflags = False
    plotsymbol = 'o'
    plotcolor = 'blue'
    markersize = 5.0
    fontsize = 10.0
    showgui = False
    figfile = filename
    async = False
    plotcal()
