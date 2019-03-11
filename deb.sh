#!/bin/bash

DEB_CAR=deb_car
DEB_REMOTE=deb_remote
DEBIAN_CAR=$DEB_CAR/DEBIAN
DEBIAN_REMOTE=$DEB_REMOTE/DEBIAN
BUILD_DIR=.

PATH_CAR=$DEB_CAR/usr/local/car
PATH_REMOTE=$DEB_REMOTE/usr/local/car

chmod 755 $DEB_CAR/*
chmod 755 $DEBIAN_CAR/*

chmod 755 $DEB_REMOTE/*
chmod 755 $DEBIAN_REMOTE/*

rm -r $PATH_CAR
mkdir -p $PATH_CAR
mkdir -p $PATH_CAR/bin/
mkdir -p $PATH_CAR/bin/src/
mkdir -p $PATH_CAR/conf/

rm -r $PATH_REMOTE
mkdir -p $PATH_REMOTE
mkdir -p $PATH_REMOTE/bin/
mkdir -p $PATH_REMOTE/bin/src/
mkdir -p $PATH_REMOTE/conf/

cp -r --parents bin/car.py $PATH_CAR/
cp -r --parents bin/src/*.py $PATH_CAR/
cp -r --parents conf/*.default $PATH_CAR/

cp -r --parents bin/remote.py $PATH_REMOTE/
cp -r --parents bin/src/*.py $PATH_REMOTE/
cp -r --parents conf/*.default $PATH_REMOTE/
cp -r --parents icon/* $PATH_REMOTE/

dpkg-deb --build $DEB_CAR $BUILD_DIR
dpkg-deb --build $DEB_REMOTE $BUILD_DIR



