#!/usr/bin/env python

#  Whaaw! Media Player for playing any type of media.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, os.path
from optparse import OptionParser

__sName__ = 'whaawmp'

import gettext
gettext.install(__sName__, unicode=1)
from common import useful

useful.sName = __sName__
useful.lName = _('Whaaw! Media Player')
useful.version = '0.1.10'


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
		print '%s - %s' % (useful.lName, useful.version)
		sys.exit(0)

from gui import main as whaawmp
from common import config

# Change the process name (only for python >= 2.5, or if ctypes installed)
# Though, this program requires 2.5 anyway?:
try:
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, useful.sName, 0, 0)
except:
	pass

class main:

	def __init__(self):
		## Initialises everything.
		# Option Parser
		usage = "\n  " + useful.sName + _(" [options] filename")
		(options, args) = config.clparser(OptionParser(usage)).parseArgs(HELP)
		# Set the original directory.
		self.origDir = os.getenv('HOME')
		if (len(args) > 0 and os.path.isdir(args[-1])):
			self.origDir = args[-1]

		# Open the settings.
		cfgfile = os.path.join(os.getenv('HOME'), '.config', useful.sName, 'config.ini')
		self.cfg = config.config(cfgfile)
		# Creates the window.
		self.mainWindow = whaawmp.mainWindow(self, options, args)
		
		return


main()
