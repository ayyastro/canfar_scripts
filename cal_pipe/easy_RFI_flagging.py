
import sys
import os

'''
Easier searching for good RFI flagging values
'''

try:
    vis = sys.argv[1]
except IndexError:
    vis = raw_input("Input vis? : ")

# Just want the number of SPWs
tb.open(os.path.join(vis, "SPECTRAL_WINDOW"))
nchans = tb.getcol('NUM_CHAN')
tb.close()

spws = range(len(nchans))

default('flagdata')

for spw in spws:
    print("On spw "+str(spw)+" of "+str(len(nchans)))
    freqdevscale = 4.0
    timedevscale = 4.0
    while True:

        print("Starting at ")
        flagdata(vis=vis, mode='rflag', field='3C48*',
                 spw=str(spw), datacolumn='corrected',
                 action='calculate', display='both',
                 freqdevscale=freqdevscale, timedevscale=timedevscale,
                 flagbackup=False)

        adjust = True if raw_input("New thresholds? : ") == "T" else False

        if adjust:
            print("Current freqdevscale and timedevscale: %s %s" % (freqdevscale, timedevscale))
            freqdevscale = float(raw_input("New freqdevscale : "))
            timedevscale = float(raw_input("New timedevscale : "))
        else:
            break
