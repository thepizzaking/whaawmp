#! /usr/bin/env python

#  A video thumbnailer for use with whaawmp.
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

__sName__ = 'whaaw-thumbnailer'

try:
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, __sName__, 0, 0)
except:
	pass

import sys, os, os.path
from optparse import OptionParser
import gettext
gettext.install('whaawmp', unicode=1)

import gobject
import pygst
pygst.require('0.10')
import gst
import pygtk
pygtk.require('2.0')
import gtk

class main:
	def createPlayer(self):
		self.player = gst.element_factory_make('playbin', 'player')
		
		bin = gst.Bin('video')
		filter = gst.element_factory_make('capsfilter', 'filter')
		bin.add(filter)
		filter.set_property('caps', gst.Caps('video/x-raw-rgb, depth=24, bpp=24'))
		ghostpad = gst.GhostPad("sink", filter.get_pad("sink"))
		bin.add_pad(ghostpad)
		vSink = gst.element_factory_make('fakesink', 'vsink')
		vSink.set_property('signal-handoffs', True)
		bin.add(vSink)
		pad = vSink.get_pad("sink")
		pad.add_buffer_probe(self.onBufferProbe)
		gst.element_link_many(filter, vSink)
		self.player.set_property('video-sink', bin)
		
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.watchID = self.bus.connect("message", self.onMessage)
		
		self.player.set_property('uri', self.options.uri)
		
		self.player.set_state(gst.STATE_PAUSED)
	
	
	def onBufferProbe(self, pad, buffer):
		if (self.getThumb):
			caps = buffer.caps
			filters = caps[0]
			w = filters["width"]
			h = filters["height"]
			pixbuf = gtk.gdk.pixbuf_new_from_data(buffer.data, gtk.gdk.COLORSPACE_RGB, False, 8, w, h, w*3)
			pixbuf.save(self.options.output, 'png')
			sys.exit(0)
		return True
	
	def onMessage(self, bus, message):
		if (message.src == self.player):
			if (message.type == gst.MESSAGE_ERROR):
				print _("An error ocurred")
				print message.parse_error()
				sys.exit(1)
			elif (message.type == gst.MESSAGE_STATE_CHANGED):
				old, new, pending = message.parse_state_changed()
				if (new == gst.STATE_PAUSED and self.firstPause):
					dur = self.player.query_duration(gst.FORMAT_TIME)[0]
					pos = dur * 0.3
					self.getThumb = True
					res = self.player.seek(1.0, gst.FORMAT_TIME,
					                       gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
					                       gst.SEEK_TYPE_SET, pos,
					                       gst.SEEK_TYPE_NONE, 0)
					if (not res):
						print _("An error ocurred")
						sys.exit(1)
					self.firstPause = False
	
	
	def __init__(self):
		self.firstPause = True
		self.getThumb = False
		
		parser = OptionParser("\n  " + __sName__ + _(" [options] input-file"))
		# Add parser options.
		parser.add_option("-u", "--uri", dest="uri",
		                  default=None, metavar="URI",
		                  help=_("The URI of the file to be thumbnailed"))
		parser.add_option("-o", "--output", dest="output",
		                  default=None, metavar="FILE",
		                  help=_("The destination of the resulting thumbnail"))
		parser.add_option("-p", "--position", dest="pos",
		                  default=0.3, metavar="FRAC",
		                  help=_("The position (Fraction) to take the thumbnail from (default 0.3)"))
		options, args = parser.parse_args()
		
		if (not options.output or (not options.uri and len(args) == 0)):
			print _('Sorry, a URI and output file are required to be passed.')
			sys.exit(1)
		
		self.options = options
		
		self.createPlayer()
		
		self.loop = gobject.MainLoop()
		self.loop.run()


main()
