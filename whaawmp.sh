#!/bin/sh

WHAAWDIR=$(dirname $0)/src
exec python3 ${WHAAWDIR}/whaawmp.py "$@"
