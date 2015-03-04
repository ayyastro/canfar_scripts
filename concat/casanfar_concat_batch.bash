#!/bin/bash
echo 'Making dirs'
mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}
echo 'Mount VOS in readonly mode'

# Source bash profile
source /home/ekoch/.bash_profile

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Clone CANFAR repo
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088_20141211_1418355329562 --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache --readonly
echo 'Run casapy'
cd ${TMPDIR}/proc
sudo /home/ekoch/casa-stable-4.4.95/casapy --nogui -c /home/ekoch/canfar_scripts/concat/casanfar_concat.py
echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
sudo mountvofs --vospace vos:vos:MWSynthesis/VLA/14B-088_20141211_1418355329562/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
sudo cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
sudo fusermount -u ${TMPDIR}/vos
