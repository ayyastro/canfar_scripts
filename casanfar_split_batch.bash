#!/bin/bash
echo 'Making dirs'
mkdir -p /staging/tmp/{vos,vos_cache,proc}
echo 'Mount VOS in readonly mode'

# Clone CANFAR repo
git clone https://github.com/e-koch/canfar_scripts.git

sudo mountvofs --vospace vos:MWSynthesis/VLA/14B-088_20141211_1418355329562 --mountpoint /staging/tmp/vos --cache_dir /staging/tmp/vos_cache --readonly
echo 'Run casapy'
cd /staging/tmp/proc
casapy -c /home/ekoch/canfar_scripts/casanfar_split.py
echo 'Unmount VOS'
sudo fusermount -u /staging/tmp/vos
echo 'Mount VOS'
sudo mountvofs --vospace vos:vos:MWSynthesis/VLA/14B-088_20141211_1418355329562/ --mountpoint /staging/tmp/vos --cache_dir /staging/tmp/vos_cache
echo 'Copy files to VOS'
cp -rf /staging/tmp/proc/* /staging/tmp/vos/
echo 'Unmount VOS'
sudo fusermount -u /staging/tmp/vos
