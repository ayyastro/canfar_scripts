#!/bin/bash

# Source bash profile
source /home/ekoch/.bash_profile
source /home/ekoch/.bashrc

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Get certificate
getCert

echo 'Making dirs'
chmod 777 ${TMPDIR}
mkdir -p -m 777 ${TMPDIR}/{vos,vos_cache,proc,vos_link}
chown -R ${USER} ${TMPDIR}/{vos,vos_cache,proc,vos_link}
echo 'Mount VOS in readonly mode'

# Clone CANFAR repo
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088/14B-088_20141021_1413960928386/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache --readonly

# Move to processing directory
cd ${TMPDIR}/proc

# Copy the pipeline restore file here
sudo cp ${TMPDIR}/vos/pipeline_shelf.restore .

# Update the necessary paths, then copy back over
sudo python update_pipeline_paths.py pipeline_shelf.restore ${TMPDIR}/vos /home/ekoch/pipe_scripts
sudo cp pipeline_shelf.restore ${TMPDIR}/vos/

# Specify MSfile
ms_folder='14B-088_20141021_1413960928386/'
ms_file='14B-088.sb29701604.eb29882607.56952.08797296297.ms'

full_path=$ms_folder'products/'$ms_file

# Start up the fake display for CASA
Xvfb :1 & export DISPLAY=:1

# Run the code
echo Run casapy and spw_plots.py
suod casapy --nogui --nologger -c /home/ekoch/canfar_scripts/spw_plots.py full_path

mkdir 'spw_plots'
mv *.png spw_plots

# Unmount VOSpace and copy output back over.
echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088/14B-088_20141021_1413960928386/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
sudo cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
