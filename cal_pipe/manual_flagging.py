
import sys

'''
Plot visibility data for each spw to allow for easy manual flags
'''

try:
    vis = sys.argv[1]
    field = sys.argv[2]
    corrstring = sys.argv[3]
except IndexError:
    vis = raw_input("MS Name? : ")
    field = raw_input("Field Name/Number? : ")
    corrstring = raw_input("Corrstring? : ")

tb.open(vis + '/SPECTRAL_WINDOW')
freqs = tb.getcol('REF_FREQUENCY')
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(0, len(freqs))


for spw in spws:
    nchan = nchans[spw]

    print "On " + str(spw+1) + " of " + str(len(freqs))

    default('plotms')
    vis = vis
    xaxis = 'channel'
    yaxis = 'amp'
    ydatacolumn = 'corrected'
    selectdata = True
    field = field
    spw = str(spw)
    correlation = corrstring
    averagedata = True
    avgtime = '1e8s'
    avgscan = False
    transform = False
    extendflag = False
    iteraxis = ''
    coloraxis = 'antenna2'
    plotrange = []
    xlabel = ''
    ylabel = ''
    showmajorgrid = False
    showminorgrid = False
    plotms()

    raw_input("Continue?")

    default('plotms')
    vis = vis
    xaxis = 'channel'
    yaxis = 'phase'
    ydatacolumn = 'corrected'
    selectdata = True
    field = field
    spw = str(spw)
    correlation = corrstring
    averagedata = True
    avgtime = '1e8s'
    avgscan = False
    transform = False
    extendflag = False
    iteraxis = ''
    coloraxis = 'antenna2'
    plotrange = []
    xlabel = ''
    ylabel = ''
    showmajorgrid = False
    showminorgrid = False
    plotms()

    raw_input("Continue?")

    default('plotms')
    vis = vis
    xaxis = 'time'
    yaxis = 'amp'
    ydatacolumn = 'corrected'
    selectdata = True
    field = field
    spw = str(spw)
    correlation = corrstring
    averagedata = True
    avgchannel = str(nchan)
    avgscan = False
    transform = False
    extendflag = False
    iteraxis = ''
    coloraxis = 'antenna2'
    plotrange = []
    xlabel = ''
    ylabel = ''
    showmajorgrid = False
    showminorgrid = False
    plotms()

    raw_input("Continue?")

    default('plotms')
    vis = vis
    xaxis = 'time'
    yaxis = 'phase'
    ydatacolumn = 'corrected'
    selectdata = True
    field = field
    spw = str(spw)
    correlation = corrstring
    averagedata = True
    avgchannel = str(nchan)
    avgscan = False
    transform = False
    extendflag = False
    iteraxis = ''
    coloraxis = 'antenna2'
    plotrange = []
    xlabel = ''
    ylabel = ''
    showmajorgrid = False
    showminorgrid = False
    plotms()

    raw_input("Continue?")

    default('plotms')
    vis = vis
    xaxis = 'uvwave'
    yaxis = 'amp'
    ydatacolumn = 'corrected'
    selectdata = True
    field = field
    spw = str(spw)
    correlation = corrstring
    averagedata = True
    avgchannel = str(nchan)
    avgtime = '1e8s'
    avgscan = False
    transform = False
    extendflag = False
    iteraxis = ''
    coloraxis = 'antenna2'
    plotrange = []
    xlabel = ''
    ylabel = ''
    showmajorgrid = False
    showminorgrid = False
    plotms()

    raw_input("Continue?")
