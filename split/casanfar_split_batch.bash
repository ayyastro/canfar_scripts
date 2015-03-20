#!/bin/bash

###########################
# {1} is path to MS in VOS
# {2} is name of MS
###########################

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

echo 'Mount data'
mount_data

cd ${TMPDIR}/proc

echo "Make sure inputted MS is correct"
ls -al ${TMPDIR}/vos
echo ${2}

echo 'Run casapy'
casapy --nogui -c /home/ekoch/canfar_scripts/split/casanfar_split.py ${1}/products/ ${2}


sudo fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:MWSynthesis/VLA/14B-088/${1}/products/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
