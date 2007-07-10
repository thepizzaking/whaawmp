#!/usr/bin/env python

#  A player module for gstreamer.
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
import useful


class player:
	colourSettings = False
	aspectSettings = False
	
	def play(self):
		# Starts the player playing.
		self.player.set_state(gst.STATE_PLAYING)
	
	def pause(self):
		# Pauses the player.
		self.player.set_state(gst.STATE_PAUSED)
	
	def stop(self):
		# Stops the player.
		self.player.set_state(gst.STATE_READY)
	
	
	def isPlaying(self):
		# Returns true if the player is playing, false if not.
		return self.getState() == gst.STATE_PLAYING
		
	def isStopped(self):
		# Returns true if the player is stopped, false if not.
		return (self.getState() in [ gst.STATE_NULL, gst.STATE_READY ])
	
	def isPaused(self):
		# Returns true if the player is paused, false if not.
		return self.getState() == gst.STATE_PAUSED
	
	def playingVideo(self):
		# If current-video is -1, a video is not playing.
		return (self.player.get_property('current-video') != -1 or self.player.get_property('vis-plugin') != None)
	
	
	def getState(self):
		# Returns the state of the player.
		return self.player.get_state()[1]
	
	
	def getTimesSec(self):
		## Returns the times, played seconds and duration.
		return self.getPlayedSec(), self.getDurationSec()
	
	def getPlayedSec(self):
		# Returns the played seconds.
		return useful.nsTos(self.getPlayed())
	
	def getDurationSec(self):
		# Returns the total duration seconds.
		return useful.nsTos(self.getDuration())
	
	def getPlayed(self):
		# Returns the played time (not in seconds).
		return float(self.player.query_position(gst.FORMAT_TIME)[0])
	
	def getDuration(self):
		# Returns the duration (not in seconds).
		try:
			return float(self.player.query_duration(gst.FORMAT_TIME)[0])
		except:
			return -1
	
	def getStreamsInfo(self):
		# Returns an array of stream information.
		return self.player.get_property('stream-info-value-array')
	
	
	def seekFrac(self, frac):
		# Seek from a fraction.
		self.seek(self.getDuration() * frac)
	
	def seek(self, loc):
		## Seeks to a set location in the track.
		# Set up the event for the seek.
		e = gst.event_new_seek(1.0, gst.FORMAT_TIME,
		    gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
		    gst.SEEK_TYPE_SET, loc,
		    gst.SEEK_TYPE_NONE, 0)
		
		# Send the event.
		self.player.send_event(e)
	
	
	def setURI(self, uri):
		# Sets the player's uri to the one specified.
		self.player.set_property('uri', uri)
	
	def getURI(self):
		return self.player.get_property('uri')
	
	
	def prepareImgSink(self, bus, message, far, b, c, h, s):
		# Sets the image sink.
		self.imagesink = message.src
		# Sets force aspect ratio, brightness etc according to options passed.
		self.setForceAspectRatio(far)
		self.setBrightness(b)
		self.setContrast(c)
		self.setHue(h)
		self.setSaturation(s)
	
	
	def setImgSink(self, widget):
		## Sets the video output to the desired widget.
		self.imagesink.set_xwindow_id(widget.window.xid)
	
	def setForceAspectRatio(self, val):
		## Toggles force aspect ratio on or off.
		if (self.aspectSettings):
			self.imagesink.set_property('force-aspect-ratio', val)
	
	def setBrightness(self, val):
		## Sets the brightness of the video.
		if (self.colourSettings):
			self.imagesink.set_property('brightness', val)
	
	def setContrast(self, val):
		## Sets the contrast of the video.
		if (self.colourSettings):
			self.imagesink.set_property('contrast', val)
	
	def setHue(self, val):
		## Sets the hue of the video.
		if (self.colourSettings):
			self.imagesink.set_property('hue', val)
	
	def setSaturation(self, val):
		## Sets the saturation of the video.
		if (self.colourSettings):
			self.imagesink.set_property('saturation', val)
	
	
	def setAudioSink(self, sinkName):
		## Sets the player's audio sink.
		# If a name was passed, create the element, otherwise pass None
		sink = gst.element_factory_make(sinkName, 'audio-sink') if (sinkName) else None
		# Set the player's sink accordingly.
		self.player.set_property('audio-sink', sink)
	
	def setVideoSink(self, sinkName):
		## Sets the player's video sink.
		# If a name was passed, create the element, otherwise pass None
		sink = gst.element_factory_make(sinkName, 'video-sink') if (sinkName) else None
		# Set the player's sink accordingly.
		self.player.set_property('video-sink', sink)
		# Flag the colour settings and aspect settings accordingly.
		self.colourSettings = (sinkName in [None, 'xvimagesink'])
		self.aspectSettings = (sinkName in [None, 'xvimagesink', 'ximagesink'])
	
	
	def enableVisualisation(self):
		# Enable the visualisaion.
		self.player.set_property('vis-plugin', gst.element_factory_make('goom'))
	
	def disableVisualisation(self):
		# Diable the visualisaion.
		self.player.set_property('vis-plugin', None)
	
	
	def getBus(self):
		## Gets and returns the bus of the player.
		bus = self.player.get_bus()
		
		return bus
	
	
	def setVolume(self, vol):
		## Sets the volume to the requested percentage.
		self.player.set_property('volume', vol / 100)
	
	
	def setAudioTrack(self, track):
		## Sets the audio track to play.
		self.player.set_property('current-audio', track)
	
	
	def getAudioTrack(self):
		## Gets the current audio track.
		return self.player.get_property('current-audio')
	
	
	def setSubtitleTrack(self, track):
		## Sets the subtitle track to play.
		self.player.set_property('current-text', track)
	
	
	def __init__(self):
		## Creates and prepares a player.
		# Create the player.
		self.player = gst.element_factory_make("playbin", "player")
		
		# Make the program emit signals.
		bus = self.getBus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
