# -*- coding: utf-8 -*-

#  A player module for gstreamer.
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

import sys
import pygst
pygst.require('0.10')
import gst
from common import lists, useful
from common.config import cfg


class Player:
	version = gst.gst_version
	speed = 1
	imagesink = None
	
	def play(self):
		# Starts the player playing, only if the player has a URI.
		if (self.getURI()):
			self.player.set_state(gst.STATE_PLAYING)
			return True
		return False
	
	def pause(self):
		# Pauses the player, only if the player has a URI.
		if (self.getURI()):
			self.player.set_state(gst.STATE_PAUSED)
			return True
		return False
	
	def stop(self):
		# Stops the player.
		self.player.set_state(gst.STATE_READY)
	
	def stopCompletely(self):
		# Stops the player completely (ie -> NULL).
		self.player.set_state(gst.STATE_NULL)
	
	def togglePlayPause(self):
		# Toggles play/pause.
		if (not self.getURI()):
			# If no file is currently opened, return an error.
			return False
		
		if (self.isPlaying()):
			# If the player is playing, pause the player.
			self.pause()
		else:
			# If it's already paused (or stopped with a file): play.
			self.play()
		return True
	

	def playingVideo(self):
		# If current-video is -1, a video is not playing.
		return (self.player.get_property('current-video') != -1 or self.player.get_property('vis-plugin') != None)
	
	# Returns true if the player is playing, false if not.
	isPlaying = lambda self: self.getState() == gst.STATE_PLAYING
	# Returns true if the player is stopped, false if not.
	isStopped = lambda self: (self.getState() in [ gst.STATE_NULL, gst.STATE_READY ])
	# Returns true if the player is paused, false if not.
	isPaused = lambda self: self.getState() == gst.STATE_PAUSED
	
	# Returns the bus of the player.
	getBus = lambda self: self.player.get_bus()
	# Gets the current audio track.
	getAudioTrack = lambda self: self.player.get_property('current-audio')
	# Returns the state of the player (add timeout so we don't wait forever).
	getState = lambda self: self.player.get_state(timeout=200*gst.MSECOND)[1]
	# Returns the current URI.
	getURI = lambda self: self.player.get_property('uri')
	# Returns an array of stream information.
	getStreamsInfo = lambda self: self.player.get_property('stream-info-value-array')
	
	# Returns the times, played seconds and duration.
	getTimesSec = lambda self: (self.getPlayedSec(), self.getDurationSec())
	# Returns the played seconds.
	getPlayedSec = lambda self: useful.nsTos(self.getPlayed())
	# Returns the total duration seconds.
	getDurationSec = lambda self: useful.nsTos(self.getDuration())

	def getPlayed(self):
		# Returns the played time (in nanoseconds).
		try:
			return self.player.query_position(gst.FORMAT_TIME)[0]
		except:
			return 0
	
	def getDuration(self):
		# Returns the duration (nanoseconds).
		try:
			return self.player.query_duration(gst.FORMAT_TIME)[0]
		except:
			return 0
	
	def changeSpeed(self, speed):
		# Changes the playing speed of the player.
		# Set the default speed.
		self.speed = speed
		# Seek to the current position (this will initiate the new speed).
		self.seek(self.getPlayed())
	
	def seekFrac(self, frac):
		# Seek from a fraction.
		dur = self.getDuration()
		# getDuration returns 0 on error, shouldn't seek on -1 either.
		if (dur > 0):
			self.seek(int(self.getDuration() * frac))
		
	def seek(self, loc):
		## Seeks to a set location in the track.
		# Seek to the requested position.
		self.player.seek(self.speed, gst.FORMAT_TIME,
		    gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
		    gst.SEEK_TYPE_SET, loc,
		    gst.SEEK_TYPE_NONE, 0)
	
	
	def setURI(self, uri):
		# Sets the player's uri to the one specified.
		self.player.set_property('uri', uri)
	
	
	def prepareImgSink(self, bus, message, far=True, b=0, c=1, h=0, s=1):
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
		try:
			id = widget.window.xid
		except AttributeError:
			id = widget.window.handle # win32
		self.imagesink.set_xwindow_id(id)
	
	def setForceAspectRatio(self, val):
		## Toggles force aspect ratio on or off.
		try:
			if (self.imagesink): self.imagesink.set_property('force-aspect-ratio', val)
		except TypeError:
			pass
	
	def setBrightness(self, val):
		## Sets the brightness of the video.
		self.colourBalance.set_property('brightness', val)
	
	def setContrast(self, val):
		## Sets the contrast of the video.
		self.colourBalance.set_property('contrast', val)
	
	def setHue(self, val):
		## Sets the hue of the video.
		self.colourBalance.set_property('hue', val)
	
	def setSaturation(self, val):
		## Sets the saturation of the video.
		self.colourBalance.set_property('saturation', val)
	
	
	def setAudioSink(self, sinkName=None):
		## Sets the player's audio sink.
		if (not sinkName):
			# Get the sink name if None was passed.
			sinkName = cfg.cl.audiosink or cfg.getStr("audio/audiosink")
		# If default is selected, just use None.
		if (sinkName == "default"): sinkName = None
		
		# If a name was passed, create the element, otherwise pass None
		sink = gst.element_factory_make(sinkName, 'audio-sink') if (sinkName) else None
		# Set the selected audio device.
		device = cfg.getStr('audio/audiodevice')
		if (device != ''): sink.set_property('device', device)
		# Set the player's sink accordingly.
		self.player.set_property('audio-sink', sink)
	
	def setVideoSink(self, sinkName=None):
		## Sets the player's video sink.
		if (not sinkName):
			# Get the sink name if None was passed.
			sinkName = cfg.cl.videosink or cfg.getStr("video/videosink")
		# If default is selected, just use None.
		if (sinkName == "default"): sinkName = None
		
		# Create the sink bin.
		bin =  gst.Bin()
		# Create a filter for colour balancing & add it to the bin.
		colourBalance = gst.element_factory_make('videobalance')
		bin.add(colourBalance)
		# Convert to ffmpeg colourspace to allow more video sinks.
		colourSpace = gst.element_factory_make('ffmpegcolorspace')
		bin.add(colourSpace)
		# Create a ghostpad so I can connect to it from the playbin.
		pad = colourBalance.get_pad('sink')
		ghostPad = gst.GhostPad('sink', pad)
		bin.add_pad(ghostPad)
		# If a name was passed, create the element, otherwise pass use autosink.
		sink = gst.element_factory_make(sinkName if sinkName else 'autovideosink')
		bin.add(sink)
		# Link the elements.
		gst.element_link_many(colourBalance, colourSpace,  sink)
		
		# HACK: In Windows, scrap the bin and always use directdrawsink without
		# videobalance.
		if (sys.platform == 'win32'):
			bin = gst.element_factory_make('directdrawsink')
		
		# Actually set the player's sink.
		self.player.set_property('video-sink', bin)
		# Need to change colour settings externally.
		self.colourBalance = colourBalance
	
	def setVisualisation(self, enable):
		# A call to enable or disable the visualisations from a passed boolean.
		if enable:
			self.enableVisualisation()
		else:
			self.disableVisualisation()
	
	def enableVisualisation(self):
		# Enable the visualisaion.
		self.player.set_property('vis-plugin', gst.element_factory_make('goom'))
	
	def disableVisualisation(self):
		# Diable the visualisaion.
		# FIXME: Make it so it doesn't restart the stream on disabling visualisations.
		wasPlaying = False
		if (self.isPlaying()):
			# If we're playing, stop.
			self.stop()
			wasPlaying = True
		# Disable the plugin, then start the player again (if it was playing).
		self.player.set_property('vis-plugin', None)
		if (wasPlaying): self.play()
	
	
	def setVolume(self, vol):
		## Sets the volume to the requested value.
		self.player.set_property('volume', vol)
	
	
	def setAudioTrack(self, track):
		## Sets the audio track to play.
		self.player.set_property('current-audio', track)
	
	
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
		
		# Enable the visualisation if requested.
		self.setVisualisation(cfg.getBool("gui/enablevisualisation"))

player = Player()
