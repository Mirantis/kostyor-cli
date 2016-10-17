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

# Use Alembic to build up the database
alembic -c $KOSTYOR_DIR/kostyor/db/migrations/alembic.ini upgrade head
python $KOSTYOR_DIR/tools/create_initial_data.py
python kostyor/rest_api.py &
