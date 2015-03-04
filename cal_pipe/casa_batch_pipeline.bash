#!/bin/bash

# Grab the certificate
echo Get certificate
getCert

# Make some temporary directories
echo "Making dirs"
mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}

# Specify MSfile
ms_folder='14B-088_20141021_1413960928386/products'

# Mount VOSpace
echo "Mount VOS in readonly mode"
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${ms_folder} --mountpoint ${TMPDIR}/vos --ca$

# Load in casa pointer
echo Sourcing
source /home/cloud-user/.bashrc

# Copy the necessary code
cd ${TMPDIR}/proc

git clone https://github.com/e-koch/hi_reduction_scripts.git
git checkout EVLA_pipeline

mkdir EVLA_pipeline1.3.0
cp hi_reduction_scripts/m33_evla/EVLA_pipeline1.3.0/* EVLA_pipeline1.3.0/

# Remove repo to preserve as much storage space as possible.
rm -rf hi_reduction_scripts/

# Run the code
echo 'Run VLA Pipeline'
casapy --nogui --nologger -c EVLA_pipeline.py

# Make new products folder to avoid saving over the original
echo "Making new products directory"
vmkdir vos:MWSynthesis/VLA/14B-088/${ms_folder}_new

# Unmount VOSpace and copy output back over.
echo 'Unmount VOS'
fusermount -zu ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${ms_folder}_new --mountpoint ${TMPDIR}/vos --ca$
echo 'Copy files to VOS'
cp -rf ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -zu ${TMPDIR}/vos