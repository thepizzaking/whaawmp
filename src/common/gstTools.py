#!/usr/bin/env python

#  A few gstreamer tools that I thought I could use.
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

import pygst
pygst.require('0.10')
import gst

def streamType(stream):
	## Returns the stream type as a string from a given stream.
	t = stream.get_property('type')
	types = { 0 : 'unknown',
	          1 : 'audio',
	          2 : 'video',
	          3 : 'text',
	          4 : 'element' }
	return types[t]


def messageType(message):
	## Returns the message type as a string.
	types = { gst.MESSAGE_EOS : 'eos',
	          gst.MESSAGE_ERROR : 'error',
	          gst.MESSAGE_STATE_CHANGED : 'state_changed' }
	# Try and return the corresponding sting, if it's not listed, return 'other'.
	try:
		return types[message.type]
	except KeyError:
		return 'other'


## State change checkers, msg[0] is old, [1] is new, [2] is pending.
def isPlayMsg(msg):
	## Checks if the player has just started playing.
	# The player's state always goes from Paused to Playing on start,
	# even if it was stopped.
	return (msg[0] == gst.STATE_PAUSED and msg[1] == gst.STATE_PLAYING)

def isPauseMsg(msg):
	## Checks if the player has just paused playing.
	# This will also return true on a pause, since stop also emits this
	# pattern, which is probably good.
	return (msg[0] == gst.STATE_PLAYING and msg[1] == gst.STATE_PAUSED)

def isStopMsg(msg):
	## Checks if the player has just stopped playing.
	# This will return true on a stop, since the player always goes to
	# paused state before stop, we only have to check this one case.
	return (msg[0] == gst.STATE_PAUSED and msg[1] == gst.STATE_READY)


def getAudioLangArray(player):
	tracks = []
	for x in player.getStreamsInfo():
		# For all streams in the file.
		if (streamType(x) == 'audio'):
			# If it's an audio stream, get the language code (If none, make it unknown)
			lang = x.get_property('language-code')
			if (lang == None): lang = _('Unknown')
			# Add it to the array.
			tracks.append(lang)
	# Return the tracks.
	return tracks
