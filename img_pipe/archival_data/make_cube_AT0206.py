
'''
From single channels, create the AT0206 HI cube.
'''

import glob
import sys
import subprocess
import os
import shutil

try:
    import casac
except ImportError:
    raise Warning("Must be run in a CASA environment.")


try:
    path = sys.argv[1]
    whichcubes = sys.argv[2]
    output_fits = True if sys.argv[3] == "True" else False
except IndexError:
    path = raw_input("Path to images? : ")
    whichcubes = raw_input("Which cube to make? : ")
    output_fits = True if raw_input("Convert to FITS? : ") == "True" else False


channels = range(10, 205)

try:
    os.mkdir("images")
    os.mkdir("residuals")
    os.mkdir("models")

    unzip = True
except OSError:
    unzip = False

if unzip:
    for chan in channels:
        subprocess.call(["tar", "-zxf",
                         os.path.join(path, "channel_"+str(chan)+"/M33_b_c_channel_"+str(chan)+".clean.image.tar.gz")])
        try:
            shutil.move("M33_b_c_channel_"+str(chan)+".clean.image", "images")
        except IOError:
            print("Missing image for channel "+str(chan))

        subprocess.call(["tar", "-zxf",
                         os.path.join(path, "channel_"+str(chan)+"/M33_b_c_channel_"+str(chan)+".clean.residual.tar.gz")])
        try:
            shutil.move("M33_b_c_channel_"+str(chan)+".clean.residual",
                        "residuals")
        except IOError:
            print("Missing residual for channel "+str(chan))

        subprocess.call(["tar", "-zxf",
                         os.path.join(path, "channel_"+str(chan)+"/M33_b_c_channel_"+str(chan)+".clean.model.tar.gz")])
        try:
            shutil.move("M33_b_c_channel_"+str(chan)+".clean.model", "models")
        except IOError:
            print("Missing model for channel "+str(chan))


# Create the image cube.
if whichcubes == "image" or whichcubes == "all":
    image_channels = glob.glob("images/*.image")

    ia.imageconcat(outfile='M33_206_b_c.image', infiles=image_channels,
                   reorder=True)

# Create the residual cube.
if whichcubes == "residual" or whichcubes == "all":
    resid_channels = glob.glob("residuals/*.residual")

    ia.imageconcat(outfile='M33_206_b_c.residual', infiles=resid_channels, reorder=True)

# Create the model cube.

if whichcubes == "model" or whichcubes == "all":
    resid_channels = glob.glob("models/*.model")

    ia.imageconcat(outfile='M33_206_b_c.model', infiles=model_channels, reorder=True)

# Convert to FITS

if output_fits:
    pass