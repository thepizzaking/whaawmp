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
gladeDir = 'src/gui'
execFiles = [ 'whaawmp', 'whaaw-thumbnailer' ]

# Try and read the PREFIX and DESTDIR enivronment variable.
try:
	destdir = os.path.abspath(os.environ['DESTDIR'])
except KeyError:
	destdir = ''

try:
	prefix = os.path.abspath(os.environ['PREFIX'])
except KeyError:
	prefix = '/usr/local'
# Create a base variable where to install all files.
base = destdir + prefix

# Change directories into the one where this script resides.
os.chdir(sys.path[0])

if (len(sys.argv) > 1):
	# If an argument was passed, it will be the target (or help)
	command = sys.argv[1].lower()
else:
	# If none were passed use all.
	command = 'all'

def makeAll():
	# Make all, called when no command was passed.
	compilePy()
	compilePO()
	print "Make finished, type './make.py install' to install."

def compilePy():
	# Compiles all the .py files into .pyc files.
	print 'Compiling all .py files'
	check(os.system('python -m compileall src'))

def compilePO():
	# Compiles all the translations (.po files)
	print 'Compiling all .po files'
	check(os.system('./po/potool.py compile'))

def makeInstall():
	# Installs the program.
	makeInstallDirs()
	installBin()
	installLocales()
	print '\n\nDone!!!'

def makeInstallDirs():
	# Makes the install directories.
	# Only need the end of the trees sinse makedirs is used.
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
	# Installs all the binary files.
	# First the desktop files to their required locations.
	install('whaawmp.desktop', '%s/share/applications' % base)
	install('whaaw-thumbnailer.desktop', '%s/share/thumbnailers' % base)
	# Images.
	install('images/*.png', '%s/share/whaawmp/images' % base)
	# The .py files used to start the program, the .pyc files of these aren't
	# used anyway.
	install('src/*.py', '%s/share/whaawmp/src' % base)
	for x in pycDir:
		# For all files in the .pyc directories.
		install('%s/*.pyc' % x, '%s/share/whaawmp/%s' % (base, x))
	# Now the gladefile too.
	x = gladeDir
	install('%s/*.glade' % x, '%s/share/whaawmp/%s' % (base, x))
	for x in execFiles:
		# For all of them in executable files list.
		# Install the file as executable
		install(x, '%s/share/whaawmp' % base, 755)
		# Open a file in /bin and put a script there.
		f = open(base + '/bin/%s' % x, 'w')
		f.write('#!/bin/sh\nexec %s/share/whaawmp/%s "$@"' % (prefix, x))
		f.close
		# Set the script to executable.
		check(os.system('chmod 755 %s/bin/%s' % (base, x)))

def installLocales():
	# Installs all the locales
	for x in os.popen('find po -name whaawmp.mo').read().split():
		# For all locales found, install them to their correct locations.
		dest = base + '/share/locale/%s' % x[2:]
		install(x, dest, args='-D')
	

def makeInstallSrc():
	# Installs the source (.py) files along with the .pyc files.
	makeInstall()
	for x in pycDir:
		# For all the directories we installed the .pyc file in, put the .py
		# files in there too.
		install('%s/*.py' % x, '%s/share/whaawmp/%s' % (base, x))


def makeUninstall():
	# Uninstalls all the program (except for locales, I'll get that tomorrow).
	os.system('rm -r %s/share/whaawmp' % base)
	os.system('rm %s/share/applications/whaawmp.desktop' % base)
	os.system('rm %s/share/thumbnailers/whaaw-thumbnailer.desktop' % base)
	os.system('rm %s/bin/whaawmp' % base)
	os.system('rm %s/bin/whaaw-thumbnailer' % base)

def install(src, dst, perm='644', args=''):
	# Installs a file with the requested attributes (checks for failure)
	perm = str(perm)
	print 'Installing %s to %s as %s' % (src, dst, perm)
	check(os.system('install %s -m %s %s %s' % (args, perm, src, dst)), 'Installation Failed!')


def check(x, msg='Fail!'):
	# Checks if an external command failed, and quits if it did.
	if (x):
		print msg
		sys.exit(1)


def printHelp(commands):
	# Prints a line about usage, then a list of available options.
	print "Usage: './main.py [option]' where option is one of:"
	for x in commands:
		print x


def __init__():
	# A list of commands.
	commands = { 'all' : makeAll,
	             'compilepy' : compilePy,
	             'compilepo' : compilePO,
	             'install' : makeInstall,
	             'makeinstalldirs' : makeInstallDirs,
	             'installsrc' : makeInstallSrc,
	             'installlocales' : installLocales,
	             'uninstall' : makeUninstall }
	
	# If the command is a help one, print help and quit.
	if (command in [ '--help', '-h', 'help']):
		printHelp(commands)
		sys.exit(0)
	
	try:
		# Try and execute the command, if it fails, quit.
		commands[command]()
	except KeyError:
		print "Could not find target '%s'" % (command)
		sys.exit(1)

__init__()
