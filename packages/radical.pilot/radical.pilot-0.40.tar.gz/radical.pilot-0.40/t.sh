#!/bin/bash

cd /tmp/
ssh stampede.tacc.xsede.org /bin/date
virtualenv ve
source ve/bin/activate
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
git checkout master
pip install --upgrade .
python examples/00_getting_started.py local.localhost
python examples/00_getting_started.py xsede.stampede

