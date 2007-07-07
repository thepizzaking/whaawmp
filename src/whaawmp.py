#!/usr/bin/env python

#  Whaaw! Media Player for playing any type of media.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys, os, os.path
from optparse import OptionParser

__sName__='whaawmp'
__lName__='Whaaw! Media Player'
__version__='0.1.5'

# Have to manually check for help here, otherwise gstreamer prints out its own help.
HELP = False
for x in sys.argv:
	# For all arguments
	if (x in ['--help', '-h']):
		#  If -h or --help is there, help is true (also remove it so gstreamer doesn't get it)
		HELP = True
		sys.argv.remove(x)
	if (x == '--version'):
		# If --version, print out the version, then quit.
		print '%s - %s' % (__lName__, __version__)
		sys.exit(0)

from gui import main as whaawmp
import config

# Change the process name (only for python >= 2.5, or if ctypes installed):
try:
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, __sName__, 0, 0)
except:
	pass

class main:

	def __init__(self):
		## Initialises everything.
		# Option Parser
		usage = "\n  " + __sName__ + " [options] filename"
		(options, args) = config.clparser(OptionParser(usage)).parseArgs(HELP)
		if (not options.force and (len(args) == 0 or not os.path.isdir(args[len(args)-1]))):
			print '\nError: It is likely that you are trying to run this player without'
			print 'using the supplied script.  Please use the script to run whaawmp.'
			print '(Or use --force to force start)'
			sys.exit()
		origDir = args[len(args)-1] # Directory from which whaawmp was called.
		# Open the settings.
		cfgfile = "%s%s.config%swhaawmp%sconfig.ini" % (os.getenv('HOME'), os.sep, os.sep, os.sep)
		self.cfg = config.config(cfgfile)
		# Set the last folder to the directory from which the program was called.
		self.lastFolder = origDir
		# Creates the window.
		self.mainWindow = whaawmp.mainWindow(self, __version__, options, args)
		
		return


main()
