#!/bin/bash

# Source bash profile
source /home/ekoch/.bash_profile
source /home/ekoch/.bashrc

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Get certificate
getCert

mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}

git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

mountvofs --vospace vos:MWSynthesis/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache

echo "Copying files onto VM"

cp ${TMPDIR}/vos/Arecibo/M33_mask.image.zip ${TMPDIR}/proc
cp ${TMPDIR}/vos/Arecibo/M33_model.image.zip ${TMPDIR}/proc

mkdir ${TMPDIR}/proc/M33_b_c.ms/
cp -R ${TMPDIR}/vos/VLA/archival/M33_b_c.ms/* ${TMPDIR}/proc/M33_b_c.ms/

# Unmount
fusermount -u ${TMPDIR}/vos

# Unzip the model and mask
unzip ${TMPDIR}/proc/M33_mask.image.zip -d ${TMPDIR}/proc
unzip ${TMPDIR}/proc/M33_model.image.zip -d ${TMPDIR}/proc

# Delete zip files
rm M33_mask.image.zip
rm M33_model.image.zip

echo "Running CASA"

cd ${TMPDIR}/proc

casapy --nogui -c /home/ekoch/canfar_scripts/img_pipe/archival_data/m33_arch_206_all_img.py


# Now remount VOS, and copy over the relevant infos
echo "Remount"
mountvofs --vospace vos:MWSynthesis/VLA/archival/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache

cp -a ${TMPDIR}/proc/casa*.log ${TMPDIR}/vos/

cp -a ${TMPDIR}/proc/M33_206_b_c.clean* ${TMPDIR}/vos/

cp -a ${TMPDIR}/proc/*.fits ${TMPDIR}/vos/

echo "Unmount"
fusermount -u ${TMPDIR}/vos