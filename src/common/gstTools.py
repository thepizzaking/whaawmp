# -*- coding: utf-8 -*-

#  A few gstreamer tools that I thought might be handy.
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

import pygst
pygst.require('0.10')
import gst

from common import lists

def streamType(stream):
	## Returns the stream type as a string from a given stream.
	return lists.gstStreamType[stream.get_property('type')]

def getAudioLangArray(player):
	# For the moment, just print n unknown languages.
	n = player.player.get_property('n-audio')
	tracks = []
	for x in range(n):
		# Add all audio streams to the list.
		lang = _('Unknown')
		tracks.append(lang)
	# Return the tracks.
	return tracks

def hasVideoTrack(player):
	## Returns true if the stream has a video track.
	if (player.player.get_property('n-video') >= 1): return True
	# Otherwise return false.
	return False
