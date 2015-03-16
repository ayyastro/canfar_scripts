#!/bin/bash

# Source bash profile
source /home/ekoch/.bash_profile
source /home/ekoch/.bashrc

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Get certificate
getCert

mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}

rm -rf /home/ekoch/canfar_scripts
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

mountvofs --vospace vos:MWSynthesis/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache

echo "Copying files onto VM"

cp ${TMPDIR}/vos/Arecibo/M33_mask.image.zip ${TMPDIR}/proc
echo "Done M33_mask"
ls -al ${TMPDIR}/proc/

cp ${TMPDIR}/vos/Arecibo/M33_model.image.zip ${TMPDIR}/proc
echo "Done M33_model"
ls -al ${TMPDIR}/proc/

mkdir -m 777 ${TMPDIR}/proc/M33_b_c.ms/
cp -R ${TMPDIR}/vos/VLA/archival/M33_b_c.ms/* ${TMPDIR}/proc/M33_b_c.ms/
echo "Done MS Set"
ls -al ${TMPDIR}/proc/
ls -al ${TMPDIR}/proc/M33_b_c.ms/

# Unmount
fusermount -u ${TMPDIR}/vos

cd ${TMPDIR}/proc

# Unzip the model and mask
unzip M33_mask.image.zip
tar -zxf M33_model.image.zip

ls -al ${TMPDIR}/proc

# Delete zip files
rm M33_mask.image.zip
rm M33_model.image.tar.gz

echo "Running CASA"

echo "Show contents"
ls -al ${TMPDIR}/proc

casapy --nogui -c /home/ekoch/canfar_scripts/img_pipe/archival_data/m33_arch_206_all_img.py


# Compress the clean output to upload to VOS

# tar -zcf M33_206_b_c.clean.flux.tar.gz M33_206_b_c.clean.flux*
tar -zcf M33_206_b_c.clean.image.tar.gz M33_206_b_c.clean.image
# tar -zcf M33_206_b_c.clean.mask.tar.gz M33_206_b_c.clean.mask
# tar -zcf M33_206_b_c.clean.model.tar.gz M33_206_b_c.clean.model
# tar -zcf M33_206_b_c.clean.psf.tar.gz M33_206_b_c.clean.psf
tar -zcf M33_206_b_c.clean.residual.tar.gz M33_206_b_c.clean.residual

# Now remount VOS, and copy over the relevant infos
echo "Remount"
mountvofs --vospace vos:MWSynthesis/VLA/archival/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache

cp -a ${TMPDIR}/proc/casa*.log ${TMPDIR}/vos/

cp -a ${TMPDIR}/proc/M33_206_b_c.clean*.tar.gz ${TMPDIR}/vos/

cp -a ${TMPDIR}/proc/*.fits ${TMPDIR}/vos/

echo "Unmount"
fusermount -u ${TMPDIR}/vos