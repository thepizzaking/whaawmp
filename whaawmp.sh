#!/bin/sh

WHAAWDIR=$(dirname $0)/src
exec python ${WHAAWDIR}/whaawmp.py "$@"
