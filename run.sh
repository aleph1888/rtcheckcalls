#! /bin/bash
cd /home/caedes/rtcheckcalls/
export PYTHONPATH=/home/caedes/rtcheckcalls/:/home/caedes/rtcheckcalls/lib/
python2.7 /usr/bin/twistd -ny main.tac
