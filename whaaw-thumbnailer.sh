#!/bin/sh

WHAAWDIR=$(dirname $0)/src
exec python2 ${WHAAWDIR}/thumbnailer.py "$@"
