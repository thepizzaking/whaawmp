# -*- coding: utf-8 -*-

#  An interface for tagging (gstreamer).
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

import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
from common import useful
from common.config import cfg
from common.gstPlayer import player


def getCurTags():
	## Gets the currently playing file's tags.
	# Read the current tags from the player (audio stream 0 only, might
	# FIXME this later).
	return player.player.emit('get-audio-tags',0)

def getDispTitle(tags):
	## Gets the display title according to configuration.
	# Flag that no tags have been added.
	noneAdded = True
	# Initialise the window's title.
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
			# Make sure we actually have a string (sometimes the tags are spat out as lists,
			# so if we have a list, just take the first one.
			if (isinstance(nStr, list)):
				nStr = nStr[0]
			if not isinstance(nStr, basestring):
				# If it's not a string, recast it as a string.
				nStr = str(nStr)
			
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
	trys = 0
	maxTrys = 5
	timer = None
	
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
		# Stop the player before anything else, and timer.
		if self.timer: Gobject.Source.remove(self.timer)
		self.player.set_state(Gst.State.READY)
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
		self.player.set_state(Gst.State.PAUSED)
		# Reset number of trys and start a timer to attempt to read the
		# tags. (every second).
		self.trys = 0
		self.timer = GObject.timeout_add_seconds(1, self.tryTags)
	
	def onMessage(self, bus, message):
		## Called when a message is emitted, from the playbin.
		if (message.type == Gst.MessageType.ERROR):
			# If we get an error, BAIL! (to next track)
			self.nextTrack()
		return
	
	def tryTags(self):
		## Trys to extract the tags from the current track.
		# Try and get the tags.
		tags = self.player.emit('get-audio-tags',0)
		# If we got tags, act on them.
		if tags: self.actOnTags(self.player.get_property('uri'), tags)
		# The return value should be true (try again) if we didn't get
		# any tags and we haven't reached maxTrys yet.
		res = (tags == None) and (self.trys < self.maxTrys)
		if not res:
			# If we're not going to try again, go to the next track.
			self.nextTrack()
		return res
	
	def actOnTags(self, uri, tags):
		## Acts accordingly when we successfully extract tags.
		if (uri == self.current['uri']):
			# Get the function and arguments associated with the current
			# track, but only if the URIs match.
			if self.player.get_property('n-video') == 0:
				isvideo = False
			else:
				isvideo = True
			func, args = self.current['func'], self.current['args']
			func(uri, tags, isvideo, *args)
		else:
			print _("Something bad happened which shouldn't\nTell me: current data did not match player URI")
	
	
	def __init__(self):
		## Need to use a playbin to read the tags.
		# Create the playbin.
		self.player = Gst.ElementFactory.make('playbin')
		# Set the audio & video sinks to fakesinks so weird things don't happen.
		self.player.set_property('video-sink', Gst.ElementFactory.make('fakesink'))
		self.player.set_property('audio-sink', Gst.ElementFactory.make('fakesink'))
		
		# Get the players bus, add signal watch and connect the onMessage function.
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.onMessage)

# So we can run commands easier.
fileTag = FileTag()
