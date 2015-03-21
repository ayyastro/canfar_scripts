#!/bin/bash

# Source bash profile
shopt -s expand_aliases
source /home/ekoch/.bash_profile

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Get certificate
getCert

echo 'Making dirs'
mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}

# Clone CANFAR repo
rm -rf /home/ekoch/canfar_scripts
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

# Input a directory where the MS is
# directory = ${1}
# msfile = ${2}

echo ${1}
echo ${2}

echo "Mount dataset"
mount_data

# Move to processing directory
cd ${TMPDIR}/proc

# Copy the pipeline restore file here
cp ${TMPDIR}/vos/${1}/products/pipeline_shelf.restore ${TMPDIR}/proc/

# Update the necessary paths
casapy --nogui --nologger -c /home/ekoch/canfar_scripts/cal_pipe/update_pipeline_paths.py pipeline_shelf.restore ${TMPDIR}/vos/${1}/products/${2} /home/ekoch/canfar_scripts/EVLA_pipeline1.3.0/

# Also copy and unzip the caltables to the working directory
cp ${TMPDIR}/vos/${1}/products/caltables.tgz ${TMPDIR}/proc
tar -xzf caltables.tgz
rm caltables.tgz

# Specify MSfile
full_path=${1}'products/'${2}

# Start up the fake display for CASA
Xvfb :1 & export DISPLAY=:1

# Run the code
echo "Run casapy and spw_plots.py"
casapy --nogui -c /home/ekoch/canfar_scripts/cal_pipe/spw_plots.py T F

echo "Print contents"
ls -al

# Delete expanded caltables
rm -rf final_caltables

mkdir -m 777 spw_plots
mv *.png spw_plots

# Don't overwrite pipeline restore file to VOS, just in case
rm pipeline_shelf.restore

# Unmount VOSpace and copy output back over.
echo 'Unmount'
sudo fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${1}/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
# Check if spw_plots already exists
if [ -d "${TMPDIR}/vos/spw_plots" ]
    then
    echo "Already contains spw_plots"
    cp ${TMPDIR}/proc/spw_plots/* ${TMPDIR}/vos/spw_plots/
else
    cp -a ${TMPDIR}/proc/spw_plots/ ${TMPDIR}/vos/
fi
# Delete plots on VM
rm -rf ${TMPDIR}/proc/spw_plots

cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
