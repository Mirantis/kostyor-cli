#!/usr/bin/env bash

set -ex

KOSTYOR_DIR='/tmp/Kostyor'

python setup.py install

if ! [ -d $KOSTYOR_DIR ]; then
    cd /tmp
    git clone https://github.com/sc68cal/Kostyor.git
else
    git -C $KOSTYOR_DIR pull
fi

cd $KOSTYOR_DIR
pip install -r requirements.txt
python setup.py install
python tools/create_database.py
python kostyor/rest_api.py &
