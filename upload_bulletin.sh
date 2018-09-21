#!/bin/bash

FILE=$1
YEAR=${FILE%%-*}
YEAR=${YEAR##*_}

chmod 644 $FILE; scp $FILE basile@christcentralsf.com:/sites/ccpc.com/files/programs/$YEAR/
