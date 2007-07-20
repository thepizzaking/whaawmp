#!/usr/bin/env python

#  Make utilities for Whaaw! Media Player.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#       This file is part of Whaaw! Media Player (whaawmp)
#
#       whaawmp is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       whaawmp is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys, os.path

# Directories where to install files from.
pycDir = [ 'src/common', 'src/gui' ]
pyDir = [ 'src' ] + pycDir
gladeDir = 'src/gui'
binFiles = [ 'whaawmp', 'whaaw-thumbnailer' ]

try:
	destdir = os.path.abspath(os.environ['DESTDIR'])
except KeyError:
	destdir = ''

try:
	prefix = os.path.abspath(os.environ['PREFIX'])
except KeyError:
	prefix = '/usr/local'
base = destdir + prefix

os.chdir(sys.path[0])

if (len(sys.argv) > 1):
	command = sys.argv[1]
else:
	command = 'all'

def makeAll():
	compilePy()
	compilePO()
	print "Make finished, type './make.py install' to install."

def compilePy():
	os.system('python -m compileall src')

def compilePO():
	os.system('./po/potool.py compile')

def makeInstall():
	makeInstallDirs()
	installBin()
	installLocales()

def makeInstallDirs():
	dirs = [ '/bin',
	         '/share/applications',
	         '/share/thumbnailers',
	         '/share/whaawmp/images',
	         '/share/whaawmp/src/common',
	         '/share/whaawmp/src/gui',
	         '/share/locale' ]
	for x in dirs:
		if (not os.path.isdir(base + x)): os.makedirs(base + x)

def installBin():
	os.system('install -m install -m 644 whaawmp.desktop %s/share/applications' % base)
	os.system('install -m install -m 644 whaaw-thumbnailer.desktop %s/share/thumbnailers' % base)
	os.system('install -m install -m 644 images/*.png %s/share/whaawmp/images' % base)
	os.system('install -m 644 src/*.py %s/share/whaawmp/src' % base)
	for x in pycDir:
		os.system('install -m 644 %s/*.pyc %s/share/whaawmp/%s' % (x, base, x))
	x = gladeDir
	os.system('install -m 644 %s/*.glade %s/share/whaawmp/%s' % (x, base, x))
	for x in binFiles:
		os.system('install -m 755 %s %s/share/whaawmp' % (x, base))
		f = open(base + '/bin/%s' % x, 'w')
		f.write('#!/bin/sh\nexec %s/share/whaawmp/%s "$@"' % (prefix, x))
		f.close
		os.system('chmod 755 %s/bin/%s' % (base, x))

def installLocales():
	for x in os.popen('find po -name whaawmp.mo').read().split():
		dest = base + '/share/locale' + x[2:]
		os.system('install -D -m 644 ' + x + ' ' + dest)
	

def makeInstallSrc():
	makeInstall()
	for x in pyDir:
		os.system('install -m 644 %s/*.py %s/share/whaawmp/%s' % (x, base, x))


def makeUninstall():
	os.system('rm -r %s/share/whaawmp' % base)
	os.system('rm %s/share/applications/whaawmp.desktop' % base)
	os.system('rm %s/share/thumbnailers/whaaw-thumbnailer.desktop' % base)
	os.system('rm %s/bin/whaawmp' % base)
	os.system('rm %s/bin/whaaw-thumbnailer' % base)


def __init__():
	commands = { 'all' : makeAll,
	             'compilepy' : compilePy,
	             'compilepo' : compilePO,
	             'install' : makeInstall,
	             'makeinstalldirs' : makeInstallDirs,
	             'installsrc' : makeInstallSrc,
	             'installlocales' : installLocales,
	             'uninstall' : makeUninstall }
	try:
		commands[command.lower()]()
	except KeyError:
		print "Could not find target '%s'" % (command)
		sys.exit(1)

__init__()
