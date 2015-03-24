#!/bin/bash
echo 'Making dirs'
mkdir -p ${TMPDIR}/{vos,vos_cache,proc,vos_link}
echo 'Mount VOS in readonly mode'

# Source bash profile
source /home/ekoch/.bash_profile

getCert

# Set username. Otherwise CASA crashes.
export USER='ekoch'

# Clone CANFAR repo
rm -rf /home/ekoch/canfar_scripts
git clone https://github.com/e-koch/canfar_scripts.git /home/ekoch/canfar_scripts

# First argument is the name of the concatenated MS file.
conc_name = ${1}

# Arguments provide the paths to the MS's. Concatenate them together to pass to python script
echo "$#-1 paths provided."
conc_args = ${2}
for arg in {3..$#}
do
    conc_args+=' '${arg}
done

mountvofs --vospace vos:MWSynthesis/VLA/14B-088/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache --readonly
echo 'Run casapy'
cd ${TMPDIR}/proc
casapy --nogui -c /home/ekoch/canfar_scripts/concat/casanfar_concat.py conc_name conc_args
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
echo 'Mount VOS'
mountvofs --vospace vos:vos:MWSynthesis/VLA/14B-088/ --mountpoint ${TMPDIR}/vos --cache_dir ${TMPDIR}/vos_cache
echo 'Copy files to VOS'
cp -a ${TMPDIR}/proc/* ${TMPDIR}/vos/
echo 'Unmount VOS'
fusermount -u ${TMPDIR}/vos
