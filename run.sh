#! /bin/bash
cd /root/rtcheckcalls/
export PYTHONPATH=/root/rtcheckcalls/
twistd -ny main.tac
