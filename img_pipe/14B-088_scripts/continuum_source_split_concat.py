
'''
Split out continuum source for 14B-088
'''

import glob
import os


data_path = "/lustre/aoc/observers/nm-7669/data/continuum_final/"

output_path = "/lustre/aoc/observers/nm-7669/data/continuum_final/source_splits/"

# Get the tracks in the data_path
tracks = glob.glob(os.join(data_path, "14B-088*"))

tracks = [track[:-10]+"_source"+track[-10:]]