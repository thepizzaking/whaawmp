#!/usr/bin/env python

# Configuration Backend
# Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
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


import os, sys
from ConfigParser import SafeConfigParser
from common import lists

class config:
	def save(self):
		## Saves the configuration file.
		f = open(self.loc, "w")
		self.config.write(f)
		f.close()
	
	
	def splitOpt(self, option):
		if ('/' not in option):
			print _('Error!! No slash (/) in option, something bad happened!')
			sys.exit()
		return option.split('/')
	
	
	def get(self, loption):
		## Gets a configuration option.
		# Make it lowercase for compatability.
		loption = loption.lower()
		section, option = self.splitOpt(loption)
		# Try to get it, if it fails (option doesn't exist, set the 
		# option to the default value passed and return it.
		try:
			return self.config.get(section, option)
		except:
			self.set(loption, self.defaults[loption])
			return self.defaults[loption]
	
	
	def set(self, loption, value):
		## Sets the option value to that passed.
		# Lowercase for compatability.
		loption = loption.lower()
		section, option = self.splitOpt(loption)
		if (section not in self.config.sections()):
			# If the section doesn't exist, add it.
			self.config.add_section(section)
		
		# Set the option to the value.
		self.config.set(section, option, str(value))
	
	
	def getStr(self, option):
		## Returns the option as a string, even though this already happens.
		return self.get(option)
			
	
	def getInt(self, option):
		## Returns an option as an integer.
		res = self.get(option)
		# If the type won't go directly to an integer, try a float first.
		try:
			return int(res)
		except:
			return int(float(res))

	
	def getFloat(self, option):
		# Returns the requested option as a float.
		return float(self.get(option))
	
	
	def getBool(self, option):
		# Returns the requested option as a bool.
		res = self.get(option)
		if (str(res).lower() in ['false', '0', 'none', 'no']):
			return False
		return True
		
	
	def prepareConfDir(self, file):
		## Checks if the config directory exists, if not, create it.
		dir = os.path.dirname(file)
		if (not os.path.exists(dir)):
			os.makedirs(dir)
	
	
	def __init__(self, file):
		## Preparation.
		# Make sure the config directory exists.
		self.prepareConfDir(file)
		# Get the default settings.
		self.defaults = lists.defaultOptions()
		# Create a config parser.
		self.config = SafeConfigParser()
		# Set the config files location.
		self.loc = file
		
		# Open the config file.
		self.config.read(self.loc)



class clparser:
	## Command line parsing.
	def __init__(self, parser):
		self.parser = parser
	
	def parseArgs(self, HELP):
		# Add the options to the parser.
		self.addOptions()
		# If help was requested, print it, then exit.
		if (HELP):
			self.parser.print_help()
			sys.exit()
		# Parse the arguments and return the result.
		return self.parser.parse_args()
	
	
	def addOptions(self):
		# Activate fullscreen (only if playing a video)
		self.parser.add_option("-f", "--fullscreen",
		                       action="store_true", dest="fullscreen", default=False,
		                       help=_("Play the file in fullscreen mode"))
		# Set the volume of the player.
		self.parser.add_option("-v", "--volume", dest="volume",
		                       default=None, metavar="VOL",
		                       help=_("Sets the player's volume to VOL (0-100)"))
		# Set the audio sink to that specified.
		self.parser.add_option("--audiosink", dest="audiosink",
		                       default=None, metavar="SINK",
		                       help=_("Sets the player's audio ouput to SINK"))
		# Set the video sink.
		self.parser.add_option("--videosink", dest="videosink",
		                       default=None, metavar="SINK",
		                       help=_("Sets the player's video ouput to SINK"))
		
