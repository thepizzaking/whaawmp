#!/bin/sh

WHAAWDIR=$(dirname $0)/src
exec python -O ${WHAAWDIR}/thumbnailer.py "$@"
