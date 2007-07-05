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

from gui import main as whaawmp
import config

__pName__='whaawmp'
__version__='0.1.5'

# Change the process name (only for python >= 2.5, or if ctypes installed):
try:
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, __pName__, 0, 0)
except:
	pass

class main:

	def __init__(self):
		## Initialises everything.
		# Option Parser
		usage = "\n  " + __pName__ + " [options] filename"
		(options, args) = config.clparser(OptionParser(usage)).parseArgs()
		if (not options.force and (len(args) == 0 or not os.path.isdir(args[len(args)-1]))):
			print '\nError: It is likely that you are trying to run this player without'
			print 'using the supplied script.  Please use the script to run whaawmp.'
			print '(Or use --force to force start)'
			exit()
		origDir = args[len(args)-1] # Directory from which whaawmp was called.
		# Open the settings.
		cfgdir = "%s%s.config%swhaawmp" % (os.getenv('HOME'), os.sep, os.sep)
		cfgfile = "config.ini"
		self.cfg = config.config(cfgdir, cfgfile)
		# Set the last folder to the directory from which the program was called.
		self.lastFolder = origDir
		# Creates the window.
		self.mainWindow = whaawmp.mainWindow(self, __version__, options, args)
		
		return


main()
