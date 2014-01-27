#!/bin/sh
TEMPDIR=`mktemp -d`
CFGFILE=ripcord.conf.sample
tools/config/generate_sample.sh -b ./ -p ripcord -o $TEMPDIR
if ! diff $TEMPDIR/$CFGFILE etc/ripcord/$CFGFILE
then
    echo "E: ripcord.conf.sample is not up to date, please run tools/config/generate_sample.sh"
    exit 42
fi
