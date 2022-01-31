#!/bin/bash

ssh pi@192.168.99.1 "rm -rf ~/workspace/car"
scp -rp ../car/ pi@192.168.99.1:~/workspace/car
ssh pi@192.168.99.1 "cd ~/workspace/car && ./car.sh"
