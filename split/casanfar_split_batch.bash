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

sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088/14B-088_20141211_1418355329562/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache --readonly

sudo ls -al ${TMPDIR}/vos

echo 'Run casapy'
cd ${TMPDIR}/proc
sudo /home/ekoch/casa-stable-4.4.95/casapy --nogui -c /home/ekoch/canfar_scripts/split/casanfar_split.py

ls ${TMPDIR}/proc/
sudo ls -al ${TMPDIR}/vos

echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088/14B-088_20141211_1418355329562/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
sudo cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
