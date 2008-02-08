# -*- coding: utf-8 -*-

#  Configuration Backend
#  Copyright © 2007-2008, Jeff Bailes <thepizzaking@gmail.com>
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


import os, sys
from ConfigParser import SafeConfigParser
from common import lists, useful
import xdg.BaseDirectory

# Get the config file directory.
cfgFile = os.path.join(xdg.BaseDirectory.save_config_path(useful.sName), 'config.ini')

class config:
	def save(self):
		## Saves the configuration file.
		f = open(cfgFile, "w")
		self.config.write(f)
		f.close()
	
	
	def splitOpt(self, option):
		if ('/' not in option):
			print _("Aghh!  There was no '/' in the option!  This is a bug! Report it!\nDefaulting to 'unknown' group.")
			return 'unknown', option
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
	
	
	# Get as requested type.
	getStr = lambda self, opt: self.get(opt)
	getInt = lambda self, opt: int(float(self.get(opt)))
	getFloat = lambda self, opt: float(self.get(opt))
	getBool = lambda self, opt: str(self.get(opt)).lower() not in ['false', '0', 'none', 'no']
	
	
	def __init__(self):
		## Preparation.
		# Get the default settings.
		self.defaults = lists.defaultOptions
		# Create a config parser.
		self.config = SafeConfigParser()
		
		# Open the config file.
		self.config.read(cfgFile)

cfg = config()



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
		# Version information.
		self.parser.add_option("--version", action="store_true",
		                       help=_("Print the version and exit"))
		# Activate fullscreen (only if playing a video).
		self.parser.add_option("-f", "--fullscreen", dest="fullscreen",
		                       action="store_true", default=False,
		                       help=_("Play the file in fullscreen mode"))
		# Set the volume of the player.
		self.parser.add_option("-v", "--volume", dest="volume",
		                       default=None, metavar="VOL",
		                       help=_("Sets the player's volume to VOL (0-100)"))
		# Mute the player.
		self.parser.add_option("-m", "--mute", dest="mute",
		                       action="store_true", default=False,
		                       help=_("Mute the player"))
		# Set the audio sink to that specified.
		self.parser.add_option("--audiosink", dest="audiosink",
		                       default=None, metavar="SINK",
		                       help=_("Sets the player's audio ouput to SINK"))
		# Set the video sink.
		self.parser.add_option("--videosink", dest="videosink",
		                       default=None, metavar="SINK",
		                       help=_("Sets the player's video ouput to SINK"))
		# Quits the program when the stream finishes.
		self.parser.add_option("-q", "--quit", dest="quitOnEnd",
		                       action="store_true", default=False,
		                       help=_("Quits the player when the playing stream stops"))
		# Forces a new window if whaawmp is already running.
		self.parser.add_option("--new", dest="forceNewWin",
		                       action="store_true", default=False,
		                       help=_("Forces a new window if %s is already running" % useful.lName))
		# Forces the file passed to be queued in a previous whaawmp process.
		self.parser.add_option("--queue", dest="forceQueue",
		                       action="store_true", default=False,
		                       help=_("Forces the file passed to be queued if %s is already running" % useful.lName))
		# Forces the file to be played immediately in a previous whaawmp process.
		self.parser.add_option("--now", dest="forceNow",
		                       action="store_true", default=False,
		                       help=_("Forces the file to be played now in a previous %s process" % useful.lName))
		# Toggles play/pause on an already running process.
		self.parser.add_option("-t", "--play-pause", dest="togglePlayPause",
		                       action="store_true", default=False,
		                       help=_("Toggles play/pause on an already running %s process" % useful.lName))
		# Starts the player (of previous process).
		self.parser.add_option("--play", dest="play",
		                       action="store_true", default=False,
		                       help=_("Starts the player in an already running %s process" % useful.lName))
		# Pause the player (of previous process).
		self.parser.add_option("--pause", dest="pause",
		                       action="store_true", default=False,
		                       help=_("Pauses the player in an already running %s process" % useful.lName))
		# Stop the player (of previous process).
		self.parser.add_option("--stop", dest="stop",
		                       action="store_true", default=False,
		                       help=_("Stops the player in an already running %s process" % useful.lName))
		# Play the next track in the queue.
		self.parser.add_option("--next", dest="next",
		                       action="store_true", default=False,
		                       help=_("Skips to the next track in an already running %s process" % useful.lName))
		# Restart the playing track.
		self.parser.add_option("--previous", "--restart", dest="prev",
		                       action="store_true", default=False,
		                       help=_("Restarts the current track in an already running %s process" % useful.lName))
		# Query the informations of current track.
		self.parser.add_option("--query", dest="query",
		                       action="store_true", default=False,
		                       help=_("Querys the current track in an already running %s process" % useful.lName))
