#!/bin/bash

# Source bash profile
source /home/ekoch/.bash_profile
source /home/ekoch/.bashrc

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Get certificate
getCert

echo 'Making dirs'
mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}

# Clone CANFAR repo
rm -rf /home/ekoch/canfar_scripts
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

echo 'Mount VOS in readonly mode'

# Input a directory where the MS is
# directory = ${1}
# msfile = ${2}

echo ${1}
echo ${2}

mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${1}/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache

# Move to processing directory
cd ${TMPDIR}/proc

# Copy the pipeline restore file here
cp ${TMPDIR}/vos/pipeline_shelf.restore ${TMPDIR}/proc/

# Update the necessary paths, then copy back over
python update_pipeline_paths.py pipeline_shelf.restore ${TMPDIR}/vos /home/ekoch/canfar_scripts/EVLA_pipeline1.3.0/
# cp pipeline_shelf.restore ${TMPDIR}/vos/

# Specify MSfile
full_path=${1}'products/'${2}

# Start up the fake display for CASA
Xvfb :1 & export DISPLAY=:1

# Run the code
echo Run casapy and spw_plots.py
casapy --nogui --nologger -c /home/ekoch/canfar_scripts/spw_plots.py  # full_path

mkdir -m 777 spw_plots
mv *.png spw_plots

# Unmount VOSpace and copy output back over.
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${1}/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
