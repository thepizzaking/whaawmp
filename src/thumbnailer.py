#! /usr/bin/env python2
# -*- coding: utf-8 -*-

#  A video thumbnailer for use with whaawmp.
#  Copyright © 2007-2011, Jeff Bailes <thepizzaking@gmail.com>
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
#
#		The Whaaw! Media Player project hereby grants permission for non-GPL
#		compatible GStreamer plugins to be used and distributed together with
#       GStreamer and Whaaw! Media Player. This permission is above and beyond
#		the permissions granted by the GPL licence by which Whaaw! Media Player
#		is covered. (See COPYING file for more details)

__sName__ = 'whaaw-thumbnailer'

try:
	# Change the process name.
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, __sName__, 0, 0)
except:
	pass

import sys, os
from optparse import OptionParser
import gettext
gettext.install('whaawmp', unicode=1)

# Check for help here, so gstreamer doesn't steal --help.
# Flag HELP as false.
HELP = False
for x in sys.argv:
	if x in [ '-h', '--help' ]:
		# For all arguments, if they're --help or -h, HELP is true, then
		# remove the argument.
		HELP = True
		sys.argv.remove(x)

import pygtk, pygst
pygtk.require('2.0')
pygst.require('0.10')
import gtk, gst

class main:
	def __init__(self):
		# Flag that the player hasn't paused yet and we don't want to get the
		# thumbnail yet.
		self.pausedYet = False
		self.getThumb = False
		# Parser the command line options.
		self.parseOptions()
		#Create the player.
		self.createPlayer()
	
	
	def parseOptions(self):
		## Parses the command line options.
		# Create the parser, and set the usage.
		parser = OptionParser(usage="\n  " + __sName__ + _(" [options] -o output-file input-file"))
		# Add parser options:
		# Input file (can be an absolute or relative path).
		parser.add_option("-i", "--input", dest="input",
		                  default=None, metavar="FILE",
		                  help=_("The file to create the thumbnail of"))
		# The output file of the thumbnail.
		parser.add_option("-o", "--output", dest="output",
		                  default=None, metavar="FILE",
		                  help=_("The destination of the resulting thumbnail"))
		# The position in the video to get the thumbnail from.
		parser.add_option("-p", "--position", dest="pos",
		                  default=0.3, metavar="FRAC",
		                  help=_("The position (Fraction) to take the thumbnail from (default 0.3)"))
		# The output size.
		parser.add_option("-s", "--size", dest="size",
		                  default=None, metavar="SIZE",
		                  help=_("The destination size (in pixels)"))
		if (HELP):
			# If help is requested print it, then exit.
			parser.print_help()
			sys.exit(0)
		# Parse the options.
		options, args = parser.parse_args()
		
		if (not options.output or (len(args) == 0 and not options.input)):
			# Either an input or output file wasn't defined, so we can't continue.
			print _("Sorry, an input and output file are required to be passed.")
			print _("See '%s --help' for details") % (__sName__)
			sys.exit(1)
		# Turn the position into a float.
		if (options.size): options.size = int(options.size)
		options.pos = float(options.pos)
		if (options.pos > 1 or options.pos < 0):
			# If the position is not between 0 and 1, default to 0.3.
			print _('The requested position must be between 0 and 1, using 0.3.')
			options.pos = 0.3
		if (not options.input):
			# If the URI and the input file wasn't defined, the input file
			# should be the first item in the args list.
			options.input = args[0]
		if ('://' not in options.input):
			# If the URI was not defined, get it from the input file.
			options.input = 'file://' + os.path.abspath(options.input)
		
		# Make the option accessable from anywhere.
		self.options = options
		
	
	def createPlayer(self):
		## Creates the player.
		# Actually create a player.
		self.player = gst.element_factory_make('playbin', 'player')
		
		# Create a new bin.
		bin = gst.Bin('video')
		# Create a new filter, then add it.
		filter = gst.element_factory_make('capsfilter', 'filter')
		bin.add(filter)
		# Set the capabilities of the filter.
		filter.set_property('caps', gst.Caps('video/x-raw-rgb, depth=24, bpp=24'))
		# Add a ghostpad to the bin, so you can actually connect to it.
		ghostpad = gst.GhostPad("sink", filter.get_pad("sink"))
		bin.add_pad(ghostpad)
		# Create a fakesink and add it to the bin.
		vSink = gst.element_factory_make('fakesink', 'vsink')
		bin.add(vSink)
		# Get the videosinks sink pad, and add a buffer probe to it.
		pad = vSink.get_pad("sink")
		pad.add_buffer_probe(self.onBufferProbe)
		# Link the filter and the video-sink
		gst.element_link_many(filter, vSink)
		# Set the player's video-sink to the newly created bin.
		self.player.set_property('video-sink', bin)
		
		# Get the player's bus, add signal watch, then connect it.
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.watchID = self.bus.connect("message", self.onMessage)
		
		# Set the URI of the input file to the file passed.
		self.player.set_property('uri', self.options.input)
		# Set the player's state to paused.
		self.player.set_state(gst.STATE_PAUSED)
	
	
	def onBufferProbe(self, pad, buffer):
		if (self.getThumb):
			# If we want to capture the thumbnail.
			caps = buffer.caps
			if (caps == None):
				# If caps was none, quit.
				print _('Stream returned no caps, exiting')
				sys.exit(6)
			# Read the width and height.
			filters = caps[0]
			w = filters["width"]
			h = filters["height"]
			# Create a pixbuf from the data.
			pixbuf = gtk.gdk.pixbuf_new_from_data(buffer.data, gtk.gdk.COLORSPACE_RGB, False, 8, w, h, w*3)
			# Scale the pixbuf to the requested size (if requested).
			if (self.options.size):
				if (w > h):
					newW = self.options.size
					newH = int(h / (float(w) / newW))
				else:
					newH = self.options.size
					newW = int(w / (float(h) / newH))
				### Use gtk.gdk.INTERP_BILINEAR if this is too slow.
				pixbuf = pixbuf.scale_simple(newW, newH, gtk.gdk.INTERP_HYPER)
			# Save the pixbuf as the file requested at the command line.
			pixbuf.save(self.options.output, 'png')
			# Quit.
			sys.exit(0)
		return True
	
	def onMessage(self, bus, message):
		if (message.type == gst.MESSAGE_ERROR):
			# If it was an error, print the error and quit.
			print _("An error occurred")
			print message.parse_error()[0]
			sys.exit(1)
		if (message.src == self.player):
			# Only continue if the player is the source.
			if (message.type == gst.MESSAGE_STATE_CHANGED):
				# If it's a state change event, parse the event.
				old, new, pending = message.parse_state_changed()
				if (new == gst.STATE_PAUSED and not self.pausedYet):
					# If this is the first pause.
					# Check that there is at least one video track.
					vTracks = 0
					for x in self.player.get_property('stream-info-value-array'):
						vTracks += (x.get_property('type') == 2)
					if (not vTracks):
						# If there are no video tracks, quit.
						print _("There are no video tracks in this stream, exiting.")
						sys.exit(4)
					# Try and get the duration, if we can't, quit with an error.
					try:
						dur = self.player.query_duration(gst.FORMAT_TIME)[0]
					except:
						print _("Duration unable to be read, exiting.")
						sys.exit(3)
					# Get the requested position in nanoseconds.
					pos = dur * self.options.pos
					# Flag that we want to get the thumbnail.
					self.getThumb = True
					# Seek to the new position.
					res = self.player.seek(1.0, gst.FORMAT_TIME,
					                       gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
					                       gst.SEEK_TYPE_SET, pos,
					                       gst.SEEK_TYPE_NONE, 0)
					if (not res):
						# If the seek failed, quit with an error.
						print _("Unable to seek to requested position, exiting.")
						sys.exit(5)
					# Flag that the player has been paused.
					self.pausedYet = True
	
	



main()
# Start the main loop.
gtk.main()
