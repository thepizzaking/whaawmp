# -*- coding: utf-8 -*-

#  A few gstreamer tools that I thought might be handy.
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

import pygst
pygst.require('0.10')
import gst

from common import lists

def streamType(stream):
	## Returns the stream type as a string from a given stream.
	return lists.gstStreamType[stream.get_property('type')]


def messageType(message):
	## Returns the message type as a string.
	types = { gst.MESSAGE_EOS : 'eos',
				gst.MESSAGE_ERROR : 'error',
				gst.MESSAGE_STATE_CHANGED : 'state_changed',
				gst.MESSAGE_TAG : 'tag' }
	# Try and return the corresponding sting, if it's not listed, return 'other'.
	try:
		return types[message.type]
	except KeyError:
		return 'other'


## State change checkers, msg[0] is old, [1] is new, [2] is pending.
def isNull2ReadyMsg(msg):
	## Checks if the player was just initialised from NULL to READY.
	return (msg[0] == gst.STATE_NULL and msg[1] == gst.STATE_READY)

def isPlayMsg(msg):
	## Checks if the player has just started playing.
	# (Always goes via PAUSED)
	return (msg[0] == gst.STATE_PAUSED and msg[1] == gst.STATE_PLAYING)

def isPlay2PauseMsg(msg):
	## Checks if the player has just paused from playing.
	# (Goes via this on it's way to stop too)
	return (msg[0] == gst.STATE_PLAYING and msg[1] == gst.STATE_PAUSED)

def isStop2PauseMsg(msg):
	## Checks if the player has just paused from stopped.
	# (Does this on it's way to playing too)
	return (msg[0] == gst.STATE_READY and msg[1] == gst.STATE_PAUSED)

def isStopMsg(msg):
	## Checks if the player has just stopped playing.
	# (Goes via paused when stopping even if it was playing)
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

def hasVideoTrack(player):
	## Returns true if the stream has a video track.
	for x in player.getStreamsInfo():
		# For all streams in the file, return true if it's a video stream.
		if (streamType(x) == 'video'): return True
	# Otherwise return false.
	return False


def vsinkDef():
	## Returns the default video sink.
	for x in lists.vsinkTypes:
		# For all the vsink types, return the first one that exists.
		if (gst.element_factory_find(x)): return x
	
	return None
