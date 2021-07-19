#!/bin/bash

ssh pi@192.168.1.241 "rm -rf ~/workspace/car"
scp -rp ../car/ pi@192.168.1.241:~/workspace/car
ssh pi@192.168.1.241 "cd ~/workspace/car && ./car.sh"
