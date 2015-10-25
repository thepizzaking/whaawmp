# -*- coding: utf-8 -*-

#  A player module for gstreamer.
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

import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from common import lists, useful
from common.config import cfg


class Player:
	version = Gst.version
	speed = 1
	imagesink = None
	uri = None
	
	def play(self):
		# Starts the player playing, only if the player has a URI.
		if (self.uri):
			self.player.set_state(Gst.State.PLAYING)
			return True
		return False
	
	def pause(self):
		# Pauses the player, only if the player has a URI.
		if (self.uri):
			self.player.set_state(Gst.State.PAUSED)
			return True
		return False
	
	def stop(self):
		# Stops the player.
		self.player.set_state(Gst.State.READY)
	
	def stopCompletely(self):
		# Stops the player completely (ie -> NULL).
		self.player.set_state(Gst.State.NULL)
	
	def togglePlayPause(self):
		# Toggles play/pause.
		if (not self.uri):
			# If no file is currently opened, return an error.
			return False
		
		#  Toggle the player.
		self.pause() if (self.isPlaying()) else self.play()

		return True
	

	def playingVideo(self):
		# If current-video is -1, a video is not playing.
		return (self.player.get_property('current-video') != -1 or self.player.get_property('vis-plugin') != None)
	
	# Returns true if the player is playing, false if not.
	isPlaying = lambda self: self.getState() == Gst.State.PLAYING
	# Returns true if the player is stopped, false if not.
	isStopped = lambda self: (self.getState() in [ Gst.State.NULL, Gst.State.READY ])
	# Returns true if the player is paused, false if not.
	isPaused = lambda self: self.getState() == Gst.State.PAUSED
	
	# Gets the current audio track.
	getAudioTrack = lambda self: self.player.get_property('current-audio')
	# Returns the state of the player (add timeout so we don't wait forever).
	getState = lambda self: self.player.get_state(timeout=200*Gst.MSECOND)[1]
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
			return self.player.query_position(Gst.FORMAT_TIME)[0]
		except:
			return 0
	
	def getDuration(self):
		# Returns the duration (nanoseconds).
		try:
			return self.player.query_duration(gst.Format.TIME)[0]
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
		self.player.seek(self.speed, Gst.Format.TIME,
		    Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
		    Gst.SeekType.SET, loc,
		    Gst.SeekType.NONE, 0)
	
	
	def setURI(self, uri):
		# Sets the player's uri to the one specified.
		self.uri = uri
		self.player.set_property('uri', uri)
	
	
	def getVideoSrcDimensions(self):
		# Returns a tuple of the dimensions of the last video frame shown.
		try:
			caps = self.player.get_property('frame').get_caps()
		except AttributeError:
			caps = None
		if (not caps): return None
		return (caps[0]['width'], caps[0]['height'])
	
	
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
		sink = Gst.ElementFactory.make(sinkName, 'audio-sink') if (sinkName) else None
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
		bin =  Gst.Bin()
		# Create a filter for colour balancing & add it to the bin.
		colourBalance = Gst.ElementFactory.make('videobalance')
		bin.add(colourBalance)
		# Convert to ffmpeg colourspace to allow more video sinks.
		colourSpace = Gst.ElementFactory.make('videoconvert')
		bin.add(colourSpace)
		# Create a ghostpad so I can connect to it from the playbin.
		pad = colourBalance.get_static_pad('sink')
		ghostPad = Gst.GhostPad.new('sink', pad)
		bin.add_pad(ghostPad)
		# If a name was passed, create the element, otherwise pass use autosink.
		sink = Gst.ElementFactory.make(sinkName if sinkName else 'autovideosink')
		# Create a pad to send navigation information to the gstreamer backend.
		navPad = Gst.Pad(name="navPad", direction=Gst.PadDirection.SRC)
		bin.add_pad(navPad)
		bin.add(sink)
		# Link the elements.
		colourBalance.link(colourSpace)
		colourSpace.link(sink)
		
		# HACK: In Windows, scrap the bin and always use directdrawsink without
		# videobalance.
		if (sys.platform == 'win32'):
			bin = Gst.ElementFactory.make('directdrawsink')
		
		# Actually set the player's sink.
		self.player.set_property('video-sink', bin)
		# Need to change colour settings externally.
		self.colourBalance = colourBalance
	
	def sendNavigationClick(self, event):
		## Reacts to someone clicking on the video window.
		# Make sure we actually have a stream running.
		if (self.isStopped()): return
		# Get the current video src and sink sizes.
		srcDim = self.getVideoSrcDimensions()
		sinkDim = useful.videoWindowSize
		if (not sinkDim or not srcDim): return False
		# Translate the clicked co-ordinates to a point on the video.
		modX = event.x * (float(srcDim[0]) / sinkDim[0])
		modY = event.y * (float(srcDim[1]) / sinkDim[1])
		# Create a structure to be used for navigation.
		structure = Gst.Structure("application/x-gst-navigation")
		structure.set_value("event", "mouse-button-release")
		structure.set_value("button", event.button)
		structure.set_value("pointer_x", modX)
		structure.set_value("pointer_y", modY)
		# Actually send the navigation event to gstreamer.
		return self.player.get_property('video-sink').get_pad('navPad').send_event(Gst.Event.new_navigation(structure))

	def sendNavigationKeypress(self, keyname):
		# Reacts to someone pressing a key on the video window.
		# Create the structure.
		structure = Gst.Structure("application/x-gst-navigation")
		structure.set_value("event", "key-press")
		structure.set_value("key", keyname)
		# Send the event.
		return self.player.get_property('video-sink').get_pad('navPad').send_event(Gst.Event.new_navigation(structure))

	
	def setVisualisation(self, enable):
		# A call to enable or disable the visualisations from a passed boolean.
		if enable:
			self.enableVisualisation()
		else:
			self.disableVisualisation()
	
	def enableVisualisation(self):
		# Enable the visualisaion.
		self.player.set_property('vis-plugin', Gst.ElementFactory.make('goom'))
	
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
	
	
	def setAudioTrack(self, track):
		## Sets the audio track to play.
		self.player.set_property('current-audio', track)
	
	
	def setSubtitleTrack(self, track):
		## Sets the subtitle track to play.
		self.player.set_property('current-text', track)
	
	
	def setSubFont(self, font):
		## Sets the subtitles font.
		self.player.set_property('subtitle-font-desc', font)
	
	
	def __init__(self):
		## Creates and prepares a player.
		# Create the player.
		self.player = Gst.ElementFactory.make("playbin", "player")
		
		# Make the program emit signals.
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
		# Enable the visualisation if requested.
		self.setVisualisation(cfg.getBool("gui/enablevisualisation"))
		# Set the font for subtitles.
		self.setSubFont(cfg.get('video/subfont'))

player = Player()
