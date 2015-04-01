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

# Update the necessary paths
casapy --nogui --nologger -c /home/ekoch/canfar_scripts/cal_pipe/update_pipeline_paths.py pipeline_shelf.restore ${TMPDIR}/vos/${2} /home/ekoch/canfar_scripts/EVLA_pipeline1.3.0/

# Also copy and unzip the caltables to the working directory
cp ${TMPDIR}/vos/${1}/products/caltables.tgz ${TMPDIR}/proc
tar -xzf caltables.tgz
rm caltables.tgz

# Specify MSfile
full_path=${1}'products/'${2}

# Start up the fake display for CASA
Xvfb :1 & export DISPLAY=:1

# Run the code
echo Run casapy and spw_plots.py
casapy --nogui -c /home/ekoch/canfar_scripts/cal_pipe/spw_plots.py  T T F

echo "Print contents"
ls -al

mkdir -m 777 spw_plots
mv *.png spw_plots

# Don't overwrite pipeline restore file to VOS, just in case
rm pipeline_shelf.restore

# Unmount VOSpace and copy output back over.
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${1}/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
