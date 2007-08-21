#!/usr/bin/env python

#  Make utilities for Whaaw! Media Player.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#       This file is part of Whaaw! Media Player (whaawmp)
#
#       whaawmp is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the Licence, or
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
from optparse import OptionParser

# Directories where to install files from.
pyoDir = [ 'src/common', 'src/gui' ]
gladeDir = 'src/gui'
execFiles = [ 'whaawmp', 'whaaw-thumbnailer' ]

def makeAll():
	# Make all, called when no command was passed.
	compilePy()
	compilePO()
	print "Make finished, type './make.py install' to install."

def compilePy():
	# Compiles all the .py files into .pyo files.
	print 'Compiling all .py files'
	check(os.system('python -O -m compileall src'))

def compilePO():
	# Compiles all the translations (.po files)
	print 'Compiling all .po files'
	check(os.system('./po/potool.py compile'))

def makeInstall():
	# Installs the program.
	makeInstallDirs()
	if (not os.system('ls src/*.pyo 2> /dev/null')):
		# Install the binary files if they exist.
		installBin()
	else:
		# Otherwise, just the .py files.
		print "Whaaw! Media Player has not been compiled, only installing the .py files"
		installPy()
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
	#install('images/*.png', '%s/share/whaawmp/images' % base)
	# The .py files used to start the program, the .pyo files of these aren't
	# used anyway.
	install('src/*.py', '%s/share/whaawmp/src' % base)
	for x in pyoDir:
		# For all files in the .pyo directories.
		install('%s/*.pyo' % x, '%s/share/whaawmp/%s' % (base, x))
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
		# Check that the language was requested to be installed.
		reqLang = opt.locale in [ 'all', x[3:len(opt.locale)+3] ]
		if (reqLang): install(x, dest, args='-D')
	

def makeInstallSrc():
	# Installs the source (.py) files along with the .pyo files.
	makeInstall()
	installPy()

def installPy():
	# Copys the .py files over.
	for x in (pyoDir + ['src']):
		# For all the directories we installed the .pyo file in, put the .py
		# files in there too.
		install('%s/*.py' % x, '%s/share/whaawmp/%s' % (base, x))


def makeUninstall():
	# Uninstalls all the program.
	os.system('rm -rf %s/share/whaawmp' % base)
	os.system('rm -f %s/share/applications/whaawmp.desktop' % base)
	os.system('rm -f %s/share/thumbnailers/whaaw-thumbnailer.desktop' % base)
	os.system('rm -f %s/bin/whaawmp' % base)
	os.system('rm -f %s/bin/whaaw-thumbnailer' % base)
	for x in os.popen('find %s/share/locale -name whaawmp.mo' % base).read().split():
		os.system('rm -f %s' % x)

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

def parseOptions(commands):
	# Parses the command line options.
	# Make these variables global so we can use them later.
	global opt, destdir, prefix
	
	# Create a description ending with a list of commands.
	desc = 'Command can be one of:'
	for x in commands: desc += '  ' + x
	# Create the parser.
	parser = OptionParser(usage="Usage: './main.py [options] command'", description=desc)
	# Select the locale to install (none does none, all does all).
	parser.add_option('-l', '--locale', dest='locale',
	                  default='all', metavar='LOCALE',
	                  help='Select locale to install, none will install none, default: all')
	# The prefix to install to.
	parser.add_option('-p', '--prefix', dest='prefix',
	                  default=None, metavar='PREFIX',
	                  help='The prefix to install to')
	# The destination directory of installation.
	parser.add_option('-d', '--destdir', dest='destdir',
	                  default=None, metavar='DESTDIR',
	                  help='The destination of all installation')
	# The command to execute (can also just be added at the end).
	parser.add_option('-c', '--command', dest='command',
	                  default=None, metavar='COMMAND',
	                  help='The command to run')
	# Actually parse the arguments.
	opt, args = parser.parse_args()
	# If the locale is none, it should be None.
	if (opt.locale.lower() == 'none'): opt.locale = None
	# Get the destination directory and the prefix.
	if (opt.destdir):
		destdir = os.path.abspath(opt.destdir)
	else:
		# Try and read the DESTDIR enivronment variable.
		try:
			destdir = os.path.abspath(os.environ['DESTDIR'])
		except KeyError:
			destdir = ''
	if (opt.prefix):
		prefix = os.path.abspath(opt.prefix)
	else:
		try:
			prefix = os.path.abspath(os.environ['PREFIX'])
		except KeyError:
			prefix = '/usr/local'
	# Read all the commands into an array.
	if (not opt.command):
		if (len(args) > 0):
			opt.command = []
			for x in range(len(args)):
				opt.command.append(args[x])
		else:
			opt.command = [ 'all' ]
	else:
		opt.command = [ opt.command ]


def printHelp(commands):
	# Prints a line about usage, then a list of available options.
	print "Usage: './main.py [option]' where option is one of:"
	for x in commands:
		print x


def __init__():
	global base
	# A list of commands.
	commands = { 'all' : makeAll,
	             'compilepy' : compilePy,
	             'compilepo' : compilePO,
	             'install' : makeInstall,
	             'makeinstalldirs' : makeInstallDirs,
	             'installsrc' : makeInstallSrc,
	             'installlocales' : installLocales,
	             'uninstall' : makeUninstall }
	
	parseOptions(commands)
	# Create a base variable where to install all files.
	base = destdir + prefix
	# Change directories into the one where this script resides.
	os.chdir(sys.path[0])
	for command in opt.command:
		try:
			# Try and execute the command, if it fails, quit.
			commands[command]()
		except KeyError:
			print "Could not find target '%s'" % (command)
			sys.exit(1)

__init__()
