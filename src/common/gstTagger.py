# -*- coding: utf-8 -*-

#  An interface for tagging (gstreamer).
#  Copyright © 2007-2009, Jeff Bailes <thepizzaking@gmail.com>
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

import os
import gst
from common import useful
from common.config import cfg
from common.gstPlayer import player

# A global current tags list for reading.
curTags = [None, None]

def getCurTags():
	## Gets the currently playing file's tags.
	# If the first item isn't the current playing file, the tags are old, so return None.
	return curTags[1] if (curTags[0] == player.getURI()) else None

def getDispTitle(tags):
	# Set the tags for the current file.
	global curTags
	curTags = [player.getURI(), tags]
	# Flag that no tags have been added.
	noneAdded = True
	# Initiate the windows title.
	winTitle = ""
	for x in useful.tagsToTuple(cfg.getStr('gui/tagsyntax')):
		# For all the items in the list produced by tagsToTuple.
		# New string = the associated tag if it's a tag, otherwise just the string.
		# Remember in each x, [0] is True if [1] is a tag, False if it's not.
		try:
			nStr = tags[x[1]] if (x[0]) else x[1]
		except KeyError:
			nStr = None
		if (nStr):
			# If there was a string.
			# Flag that a tag has been added if it's a tag.
			if (x[0]): noneAdded = False
			# Add the string to the new window title.
			winTitle += nStr
	# If at least one tag was added, return the title, otherwise return None.
	if (not noneAdded):
		return winTitle
	else:
		return None


class FileTag:
	## A class for reading tags from a uri/filename.
	## Unfortunately, gstreamer only reads tags when it plays a file, so we
	## Add fakesinks and pause it so it emits the tags for us.
	lock = False
	# A queue for files waiting to be read.
	queue = []
	# A variable to hold the current file data.
	current = None
	
	def file(self, uri, function, *args):
		## Adds the file to be read.
		if ('://' not in uri): uri = 'file://' + uri
		# Add to the queue, and store the function to be called later.
		dic = {}
		dic['uri'] = uri
		dic['func'] = function
		dic['args'] = args
		self.queue.append(dic)
		# If we're not locked, read the next track.
		if (not self.lock): self.nextTrack()
	
	def nextTrack(self):
		## Read the next files tags.
		if (not len(self.queue)):
			# If the queue is empty, unlock and return.
			self.lock = False
			return
		# Otherwise, lock, add the next track to the playbin and pause (causes
		# tags to be read).
		self.lock = True
		self.current = self.queue[0]
		del self.queue[0]
		self.player.set_property('uri', self.current['uri'])
		self.player.set_state(gst.STATE_PAUSED)
	
	def onMessage(self, bus, message):
		## Called when a message is emitted, from the playbin.
		if (message.type in [gst.MESSAGE_ERROR, gst.MESSAGE_TAG]):
			# Only continue if the message was an error or a tag.
			# Read the URI, and check it matches the current URI.
			uri = self.player.get_property('uri')
			if (uri != self.current['uri']):
				print _("Something bad happened which shouldn't\nTell me: current data did not match player URI")
			elif (message.type == gst.MESSAGE_TAG):
				# If it's a tag, run the function passed in with the file.
				func, args = self.current['func'], self.current['args']
				func(uri, message.parse_tag(), *args)
				# Stop the player
				self.player.set_state(gst.STATE_READY)
			
			# Clear the current data, then read the next track.
			# FIXME: Uncommented, this causes tracebacks on some files.
			# Some files appear to emit multiple TAG messages.
			#self.current = None
			self.nextTrack()
	
	
	def __init__(self):
		## Need to use a playbin to read the tags.
		# Create the playbin.
		self.player = gst.element_factory_make('playbin2')
		# Set the audio & video sinks to fakesinks so weird things don't happen.
		self.player.set_property('video-sink', gst.element_factory_make('fakesink'))
		self.player.set_property('audio-sink', gst.element_factory_make('fakesink'))
		
		# Get the players bus, add signal watch and connect the onMessage function.
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.onMessage)

# So we can run commands easier.
fileTag = FileTag()
