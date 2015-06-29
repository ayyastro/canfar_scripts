
import sys

'''
Check for garbage points in a MS by SPW.
'''

try:
    vis_name = sys.argv[1]
    corrstring = sys.argv[2]
    starting_spw = int(sys.argv[3])
except IndexError:
    vis_name = raw_input("MS Name? : ")
    corrstring = raw_input("Corrstring? : ")
    starting_spw = int(raw_input("SPW to start at? : "))

tb.open(vis_name + '/SPECTRAL_WINDOW')
freqs = tb.getcol('REF_FREQUENCY')
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(starting_spw, len(freqs))

for spw_num in spws:

    print "On " + str(spw_num+1) + " of " + str(len(freqs))

    default('plotms')
    vis = vis_name
    xaxis = 'time'
    yaxis = 'amp'
    ydatacolumn = 'corrected'
    selectdata = True
    field = ''
    spw = str(spw_num)
    scan = bp_scan
    correlation = corrstring
    averagedata = False
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
