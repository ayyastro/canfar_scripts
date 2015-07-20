
import numpy as np
import re


ms_active = raw_input("MS? : ")
field_str = raw_input("Field? : ")


tb.open(vis+"/FIELD")
names = tb.getcol('NAME')
matches = [string for string in names if re.match(field_str, string)]
posn_matches = \
    [i for i, string in enumerate(names) if re.match(field_str, string)]

if len(matches) == 0:
    raise TypeError("No matches found for the given field string")

tb.open(ms_active)
scanNums = sorted(np.unique(tb.getcol('SCAN_NUMBER')))
field_scans = []
for ii in range(numFields):
    subtable = tb.query('FIELD_ID==%s'%ii)
    field_scans.append(list(np.unique(subtable.getcol('SCAN_NUMBER'))))
tb.close()

field_scans = [scans for i, scans in field_scans if i in posn_matches]

for ii in range(len(field_scans)):
    for jj in range(len(field_scans[ii])):

        default('plotms')
        vis = ms_active
        xaxis = 'time'
        yaxis = 'amp'
        ydatacolumn = 'corrected'
        selectdata = True
        field = ii
        scan = jj
        correlation = "RR,LL"
        averagedata = True
        avgbaseline = True
        transform = False
        extendflag = False
        plotrange = []
        title = 'Amp vs Time: Field'+matches[ii]+' Scan'+str(jj)
        xlabel = ''
        ylabel = ''
        showmajorgrid = False
        showminorgrid = False
        plotfile = 'field_'+matches[ii]+'_scan_'+str(jj)+'.png'
        overwrite = True
        showgui = False
        async = False
        plotms()
