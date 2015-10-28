# -*- coding: utf-8 -*-

#  Whaaw! Media Player main window.
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

import sys, os, signal, urllib, urlparse
import gi
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
gi.require_version('GdkX11', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GdkX11, GstVideo
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GLib, Gst, Gtk, Gdk
Gst.init(None)

from random import randint

from gui import dialogues, preferences
from gui.queue import queue
from gui import subtitles
from common import lists, useful
from common import gstTools as playerTools
from common import gstTagger as tagger
from common import dbusBus as msgBus
from common.config import cfg
from common.gstPlayer import player
from common.signals import signals

class mainWindow:
	# Set up some variables for the timers.
	tmrMin = None
	tmrSec = None
	# Holds the URI for the currently displayed window's title.
	titlesURI = None
	# Holds the xid for the video area.
	vidxid = None
	# Holds the progress bar adjustment.
	progressAdj = None
	
	
	def quit(self, widget=None, event=None):
		## Quits the program.
		# Stop the player first to avoid tracebacks.
		player.stopCompletely()
		# Restore the screensaver.
		# FIXME gi transition
		#useful.resumeScr()
		# Save the configuration to the file.
		cfg.save()
		Gtk.main_quit()
	
	
	def videoWindowDraw(self, widget, event):
		# FIXME gi transition.  Need to do something with cairo.
		# This used to be 'expose-event'.
		# Pull the dimensions etc.
		#rect = event.area
		
		# Let the whole thing be drawn upon.
		#colour = widget.get_style().black_gc
		#widget.window.do_draw_drawable(widget.window, colour,
		#                            self.pixmap, rect.x, rect.y, rect.x, rect.y, rect.width, rect.height)
		# Save the current video window size.
		#useful.videoWindowSize = self.pixmap.get_size()
		pass
	
	
	def videoWindowConfigure(self, widget, event=None):
		# FIXME gi.transition.  Pixmaps should be replaced by cairo.
		# Get the window's allocation.
		#rect = widget.get_allocation()
		
		# Make a new pixmap (does this create a leak?)
		#self.pixmap = Gdk.Pixmap.new(widget.window, rect.width, rect.height, -1)
		
		# Fill the whole thing with black so it looks nicer (better than white).
		#colour = widget.get_style().black_gc
		#self.pixmap.do_draw_rectangle(self.pixmap, colour, True, 0, 0, rect.width, rect.height)
		# Queue the drawing area.
		#widget.queue_draw()
		pass
	
	
	def videoWindowMotion(self, widget, event):
		## Called when the cursor moves over a video window.
		# If the controls aren't already shown, show them.
		self.showControls()
		# Restart the idle timer.
		self.restartIdleTimer()
	
	
	def videoWindowLeave(self, widget, event):
		## If the mouse has left the window, destroy the idle timer
		## (So when fullscreen & mouse over controls, they don't disappear)
		self.removeIdleTimer()

	def videoWindowEnter(self, widget, event):
		## Restart the idle timer as the mouse has entered the widget.
		self.restartIdleTimer()	
	
	def restartIdleTimer(self):
		## Restarts the idle timer by removing it and creating it again.
		self.removeIdleTimer()
		self.createIdleTimer()
		
	def removeIdleTimer(self):
		try:
			# Stop the timer to hide the cursor.
			GLib.source_remove(self.idleTimer)
			self.idleTimer = None
		except:
			pass
	
	def createIdleTimer(self):
		# Create the timer again, with the timeout reset.
		self.idleTimer = GLib.timeout_add(cfg.getInt("gui/mousehidetimeout"), self.hideControls)
	
	
	def showControls(self):
		## Shows the fullscreen controls (also the mouse):
		# Re show the cursor.
		self.setCursor(None, self.videoWindow)
		# Shows all the widgets that should be shown.
		if (not self.controlsShown):
			# If the controls aren't shown, show them.
			for x in lists.fsShowWMouse:
				self.wTree.get_object(x).show()
			# Flag the controls as being shown.
			self.controlsShown = True
	
	
	def hideControls(self):
		## Hides the fullscreen controls (also the mouse).
		# Hide the cursor.
		self.hideCursor(self.videoWindow)
		if (self.fsActive()):
			# Only hide the controls if we're in fullscreen.
			# Hides all the widgets that should be hidden.
			for x in lists.fsShowWMouse:
				self.wTree.get_object(x).hide()
			# Flag the controls as being hidden.
			self.controlsShown = False
		
		self.idleTimer = None
	
	
	def hideCursor(self, widget):
		## Hides the cursor.
		# Create and set a hidden cursor.
		invisible = Gdk.Cursor.new_for_display(widget.get_display(), Gdk.CursorType.BLANK_CURSOR)
		self.setCursor(invisible, widget)
	
	def setCursor(self, mode, widget):
		## Sets a cursor to the one specified.
		widget.get_property('window').set_cursor(mode)
	
	
	def activateFullscreen(self, widget=None):
		## Activates fullscreen.
		self.mainWindow.fullscreen()

	
	def deactivateFullscreen(self):
		## Deactivates the fullscreen.
		# Hide all the widgets, before we unfullscreen.
		for x in lists.hiddenFSWidgets:
			self.wTree.get_object(x).hide()
		# Unfullscreen the window when we're idle (stops weird dimensions).
		GLib.idle_add(self.mainWindow.unfullscreen)
	
	
	def toggleFullscreen(self, widget=None):
		# If the fullscreen window is shown, hide it, otherwise, show it.
		if (self.fsActive()):
			self.deactivateFullscreen()
		else:
			self.activateFullscreen()
	
	
	def setImageSink(self, widget=None):
		## Sets the image sink to 'widget' or the default if none passed.
		if (not widget): widget = self.videoWindow
		
		# Configure the video area.
		self.videoWindowConfigure(widget)
		
		# Set the image sink accordingly.
		player.setImgSink(self.vidxid)
		
		return False
	
	
	def videoWindowClicked(self, widget, event):
		# Get the event information.
		button = event.get_button()[1]
		
		if (event.type == Gdk.EventType._2BUTTON_PRESS and button == Gdk.BUTTON_PRIMARY):
			# If the window was double clicked, fullsreen toggle.
			self.toggleFullscreen()
		elif (event.type == Gdk.EventType.BUTTON_PRESS and button == Gdk.BUTTON_MIDDLE):
			# If it was middle clicked, toggle play/pause.
			self.togglePlayPause()
		else:
			# Otherwise send it to gstreamer to process.
			# (mainly for DVD menus).
			player.sendNavigationClick(event)

	
	def videoWindowScroll(self, widget, event):
		## Changes the volume on scroll up/down.
		volChange = self.volAdj.step_increment
		if (event.direction == Gdk.ScrollDirection.UP):
			self.increaseVolumeBy(volChange)
		elif (event.direction == Gdk.ScrollDirection.DOWN):
			self.increaseVolumeBy(- volChange)
	
	
	def increaseVolumeBy(self, change):
		## Increases the volume by the amount given.
		val = self.volAdj.value + change
		# Make sure the new value is withing the bounds (0 <= val <= 1)
		val = useful.toRange(val, 0, 1)
		# Adjust the volume.
		self.volAdj.value = val
	
	
	def windowKeyPressed(self, widget, event):
		## Emits signals defined in lists.keypressDict.
		# Don't process if alt or ctrl is down.
		if (event.state & Gdk.ModifierType.MOD1_MASK) or (event.state & Gdk.ModifierType.CONTROL_MASK): return
		keyname = Gdk.keyval_name(event.keyval)
		if keyname in lists.keypressDict:
			for x in lists.keypressDict[keyname]:
				signals.emit(x)
		# Also send the keypress to gstreamer in case it needs to act.
		player.sendNavigationKeypress(keyname)
	
	
	def toggleAdvancedControls(self):
		# Toggle the advanced controls.
		menuItm = self.wTree.get_object("mnuiAdvCtrls")
		menuItm.set_property('active', not menuItm.get_property('active'))
	
	
	def gotoDVDMenu(self,widget):
		# Go to the DVD menu.
		player.sendNavigationKeypress('m')

	
	def preparePlayer(self):
		## This prepares the player.
		# Get the bus and connect the signals.
		bus = player.player.get_bus()
		bus.connect('message', self.onPlayerMessage)
		bus.connect('sync-message::element', self.onPlayerSyncMessage)
		player.player.connect('about-to-finish', self.aboutToFinish)
		# Sets the sinks.
		player.setAudioSink()
		player.setVideoSink()
	
	
	def onPlayerMessage(self, bus, message):
		t = message.type
		if (t == Gst.MessageType.EOS):
			if (self.wTree.get_object("mnuiRepeatOne").get_property('active')):
				player.seek(0)
			else:
				if (self.wTree.get_object("mnuiRepeatAll").get_property('active')):
					queue.append(player.uri)
				# At the end of a stream, play next item from queue.
				# Or stop if the queue is empty.
				if (queue.length() > 0):
					self.playNext(atf=False)
				elif (self.wTree.get_object("mnuiQuitOnStop").get_property('active')):
					# Quit of the 'quit on stop' option is enabled.
					self.quit()
				else:
					# Otherwise, just stop.
					player.stop()
		
		elif (t == Gst.MessageType.ERROR):
			# On an error, empty the currently playing file (also stops it).
			self.playFile(None)
			# Show an error about the failure.
			msg = message.parse_error()
			signals.emit('error', str(msg[0]) + '\n\n' + str(msg[1]), _('Error!'))
		elif (t == Gst.MessageType.STATE_CHANGED and message.src == player.player):
			self.onPlayerStateChange(message)
		elif (t == Gst.MessageType.TAG):
			# Tags!!
			# FIXME gi transition.
			#self.setPlayingTitle(message.parse_tag())
			pass
	
	
	def onPlayerStateChange(self, message):
		# On a state change.
		msg = message.parse_state_changed()
		# Store the old and new states.
		old, new = msg[0], msg[1]
	
		if (old == Gst.State.READY and new == Gst.State.PAUSED):
			# The player has gone from stopped to paused.
			# Get the array of audio tracks.
			self.audioTracks = playerTools.getAudioLangArray(player)
			# Only enable the audio track menu item if there's more than one audio track.
			self.wTree.get_object('mnuiAudioTrack').set_property('sensitive', len(self.audioTracks) > 1)
			# Make an Adjustment object for the progress bar.
			# FIXME: Probably put this into a helper function.
			self.progressAdj = Gtk.Adjustment(value=player.getPlayedSec(), lower=0, upper=player.getDurationSec())
			# Maybe only want to do this if we can get the duration.
			self.lblDuration.set_property('visible', True)
			self.progressBar.set_adjustment(self.progressAdj)
			self.progressBar.set_property('sensitive', True)
			self.progressUpdate()
		
		elif (old == Gst.State.PAUSED and new == Gst.State.PLAYING):
			# The player has just started.
			# Set the play/pause image to pause.
			self.playPauseChange(True)
			# Create the timers.
			self.createPlayTimers()
			
		elif (old == Gst.State.PLAYING and new == Gst.State.PAUSED):
			# It's just been paused or stopped.
			self.playPauseChange(False)
			# Destroy the play timers.
			self.destroyPlayTimers()
			# Restore the screensaver (if inhibited)
			useful.resumeScr()
			# Update the progress bar.
			self.progressUpdate()
			
		elif (old == Gst.State.PAUSED and new == Gst.State.READY):
			# Stop message (goes through paused when stopping).
			# Reset the progress bar.
			self.progressUpdate()
			# Clear the title.
			self.setPlayingTitle(None)
	
	
	def onPlayerSyncMessage(self, bus, message):
		structure = message.get_structure()
		if (structure is None):
			return
		
		if (structure.get_name() == 'prepare-window-handle'):
			# If it's playing a video, set the video properties.
			# Get the properties of the video.(Brightness etc)
			far = cfg.getBool("video/force-aspect-ratio")
			b = cfg.getInt("video/brightness")
			c = cfg.getInt("video/contrast")
			h = cfg.getInt("video/hue")
			s = cfg.getInt("video/saturation")
			player.prepareImgSink(bus, message, far, b, c, h, s)
			# Set the image sink.
			self.setImageSink()
				
	
	def openDroppedFiles(self, widget, context, x, y, selection_data, info, time):
		## Opens a file after a drag and drop.
		# Split all the files that were input.
		uris = selection_data.data.strip().split()
		# Clear the current queue.
		queue.clear()
		# Add all the items to the queue.
		for uri in uris:
			path = urllib.url2pathname(urlparse.urlparse(uri)[2])
			queue.append(path)
		
		# Play the first file by calling the next function.
		self.playNext(atf=False)
		# Finish the drag.
		context.finish(True, False, time)
	
	def aboutToFinish(self, gstPlayer):
		# Queue the next item when the player is about to finish.
		self.playNext(True)
	
	def _cb_on_btnNext_clicked(self, widget=None, data=None):
		# Called when "Next" button is clicked
		# This isn't an atf action as we have to stop the current stream and
		# start a new one
		self.playNext(False)
	
	def playNext(self, atf=None):
		filename = None
		stop = None
		selection = 0
		## Plays the next file in the queue (if it exists).
		# Are we random?
		if self.wTree.get_object("mnuiRandom").get_property('active'):
			selection = randint(0, queue.length()-1)
		isvideo = queue.isTrackVideo(selection)
		# If we've just started Whaawmp, self.isvideo is None
		# in this case, disable gapless until we are sure it'll work
		if self.isvideo is None:
			filename = queue.getTrackRemove(selection)
			stop = True
		elif atf:
			# For gapless playback, both the current and next items _must_ be
			# audio only
			if not isvideo and not self.isvideo:
				filename = queue.getTrackRemove(selection)
				stop = False
		elif atf is False:
			# We are a queue of videos, or standalone files
			filename = queue.getTrackRemove(selection)
			stop = True
		if filename is not None and stop is not None:
			self.isvideo = isvideo
			self.playFile(filename, stop)
	
	def playFile(self, file, stop=True):
		## Plays the file 'file' (Could also be a URI).
		# Stop the player if requested. (Required for playbin2 and
		# changing streams midway through another).
		if stop: player.stop()
		if (file == None):
			# If no file is to be played, set the URI to None, and the file to ""
			file = ""
		# Set the now playing label to the file to be played.
		self.nowPlyLbl.set_label(os.path.basename(urllib.url2pathname(file)))
		if (os.path.exists(file) or '://' in file):
			# If it's not already a uri, make it one.
			# Also escape any # characters in the filename
			file = useful.filenameToUri(file).replace('#', '%23')
			# Set the URI to the file's one.
			player.setURI(file)
			# Try to set the subtitle track if requested.
			if cfg.getBool('video/autosub'): subtitles.trySubs(file)
			# Add the file to recently opened files.
			Gtk.RecentManager.get_default().add_item(file)
			# Start the player, if it isn't already running.
			if (not player.isPlaying()): player.play()
		
		elif (file != ""):
			# If none of the above, a bad filename was passed.
			print _("Something's stuffed up, no such file: %s") % (file)
			self.playFile(None)
	
	
	def setPlayingTitle(self, tags):
		# If the tags passed aren't 'None'.
		if (tags):
			# If we don't want to set it, return.
			if (not cfg.getBool('gui/fileastitle')): return
			# Set the title name.
			dispTitle = tagger.getDispTitle(tags)
			if (dispTitle):
				# Update the currently displayed titles URI.
				self.titlesURI = player.uri
			else:
				# Use the filename if no tags were found.
				if not (self.titlesURI == player.uri):
					# Make sure we haven't already used tags for this file.
					# If we have, we may as well continue using them.
					# Certain files send 4 or more tag signals, and
					# only one contains useful information.
					dispTitle = useful.uriToFilename(player.uri, ext=False)
				else:
					dispTitle = None
				
			titlename = dispTitle + ' - ' + useful.lName if dispTitle else None
		
		else:
			# Otherwise, the default title.
			titlename = useful.lName
			
		# Set the title.
		if titlename: self.mainWindow.set_title(titlename)
		


	def playDVD(self, title=None):
		## Plays a DVD
		# Start the player playing the DVD.
		self.playFile('dvd://%s' % (title if (title != None) else ""))
			
	
	def togglePlayPause(self, widget=None):
		## Toggles the player play/pause.
		
		if (not player.togglePlayPause()):
			# If toggling fails:
			# Check the queue.
			if (queue.length()):
				self.playNext(atf=False)
			else:
				# Otherwise show the open file dialogue.
				self.showOpenDialogue()
			return
	
	
	def minuteTimer(self):
		## A timer that runs every minute while playing.
		# Disable ScreenSaver (if option is enabled).
		if (cfg.getBool("misc/disablescreensaver") and player.player.get_property('n-video') > 0):
			# Inhibit hte screensaver, technically we only have to do this once.
			## FIXME: Only do this once
			useful.suspendScr()
		
		if player.isPlaying():
			return True
		else:
			self.tmrMin = None
			return False
	
	
	def secondTimer(self):
		# A function that's called once a second while playing.
		if (not self.seeking): self.progressUpdate()
		#TODO: fonts with subtitles.
		#print player.player.emit('get-text-pad', 0).get_property('active-pad') #.set_property('font-desc', 'Sans 30')
				
		# Causes it to go again if it's playing, but stop if it's not.
		if player.isPlaying():
			return True
		else:
			self.tmrSec = None
			return False
		
	
	def progressUpdate(self, pld=None, tot=None):
		# FIXME Trying to change this to a HScale.
		# Change the progress bar's adjustment value to new elapsed time.
		elapsed = player.getPlayedSec()
		duration = player.getDurationSec()
		if self.progressAdj: self.progressAdj.set_value(elapsed)
		self.lblElapsed.set_property('label', useful.secToStr(int(elapsed)))
		self.lblDuration.set_property('label', useful.secToStr(int(duration - (cfg.getBool('gui/showtimeremaining') * elapsed))))
		return
		## Updates the progress bar.
		if (player.isStopped()):
			# If the player is stopped, played time and total should 
			# be 0, and the progress should be 0.
			pld = tot = 0
			self.progressBar.set_fraction(0)
		else:
			# Otherwise (playing or paused), get the track time data, set
			# the progress bar fraction.
			if (pld == None or tot == None): pld, tot = player.getTimesSec()
			self.progressBar.set_fraction(pld / tot if (tot > 0) else 0)
		
		# Convert played & total time to integers
		p, t = int(pld), int(tot)
		# Add the data to the progress bar's text.
		text = ""
		text += useful.secToStr(p)
		if (tot > 0):
			text += " / "
			text += useful.secToStr(t - (cfg.getBool('gui/showtimeremaining') * p))
		self.progressBar.set_text(text)
	
	
	def onMainStateEvent(self, widget, event):
		## Acts when a state event occurs on the main window.
		fs = event.new_window_state & Gdk.WindowState.FULLSCREEN
		if (fs):
			# Hide all the widgets other than the video window.
			for x in lists.hiddenFSWidgets:
				self.wTree.get_object(x).hide()
			
			# Flag the the controls as not being shown.
			self.controlsShown = False
		else:
			# Re-show all the widgets that aren't meant to be hidden.
			for x in lists.hiddenFSWidgets:
				if (x not in lists.hiddenNormalWidgets): self.wTree.get_object(x).show()
			# Flag the controls as being shown.
			self.controlsShown = True


	def progressBarClick(self, widget, event):
		## The progress bar has been clicked.
		# Not sure what the first thing out is at the moment.
		button = event.get_button()[1]
		if (button == Gdk.BUTTON_PRIMARY and not player.isStopped() and player.getDuration()):
			# If it's button 1, it's not stopped and the duration exists: start seeking.
			self.seeking = True
			self.progressBarMotion(widget, event)
		else:
			# Otherwise do what would happen if the video window was clicked.
			self.videoWindowClicked(widget, event)
	
	
	def seekEnd(self, widget, event):
		## Sets that seeking has ended, and seeks to the position.
		if (self.seeking):
			self.seekFromProgress(widget, event)
			# Flag that seeking has stopped.
			self.seeking = False
	
	
	def seekFromProgress(self, widget, event=None, haha=None):
		# FIXME: A quick fix so that seeking works.
		# Should also remove the 'event' part once everything else is fixed.
		player.seek(useful.sTons(self.progressAdj.get_property('value')))
		return
		x, y = event.get_coords()
		# Get the width & height of the bar.
		alloc = widget.get_allocation()
		maxX = alloc.width
		maxY = alloc.height
		# Seek if cursor is still vertically over the bar.
		if (y >= 0 and y <= maxY): player.seekFrac(float(x) / maxX)
		# Update the progress bar to reflect the change.
		self.progressUpdate()
		
		
	def progressBarMotion(self, widget, event):
		## when the mouse moves over the progress bar.
		# If we're not seeking, cancel.
		if (not self.seeking): return
		# Check if the mouse button is still down, just in case we missed it.
		x, y = event.get_coords()
		button = event.get_button()[1]
		if (not button == Gdk.BUTTON_PRIMARY): self.seekEnd(widget, event)
		if (cfg.getBool("gui/instantseek")):
			# If instantaneous seek is set, seek!
			self.seekFromProgress(widget, event)
			return
		
		# Get the mouse co-ordinates, the width of the bar and the file duration.
		maxX = widget.get_allocation().width
		dur = player.getDurationSec()
		# Convert the information to a fraction, and make sure 0 <= frac <= 1
		frac = useful.toRange(float(x) / maxX, 0, 1)
		
		# Set the progress bar to the new data.
		self.progressUpdate((frac * dur), dur)
	
	def restartTrack(self, widget=None):
		## Restarts the currently playing track.
		# Just seek to 0.
		player.seek(0)
		# Update the progrss bar.
		GLib.idle_add(self.progressUpdate)
		# Make sure the player is playing (ie. if it was paused etc)
		player.play()
		
	
	def changeVolume(self, widget, value):
		# Set the new volume on player and configuration.
		player.player.set_property('volume',value)
		cfg.set("audio/volume", value)
	
	
	def playPauseChange(self, playing):
		## Changes the play/pause image according to the argument.
		# Set the size.
		size = cfg.getInt("gui/iconsize")
		# Set the icon accordingly (Not playing -> Pause button, otherwise, play.)
		img = Gtk.Image.new_from_icon_name('gtk-media-play' if (not playing) else 'gtk-media-pause', size)
		
		btn = self.wTree.get_object("btnPlayToggle")
		# Actually set the icon.
		btn.set_image(img)
		# Also set the tooltip.
		btn.set_tooltip_text(_('Pause') if (playing) else _('Play'))
		# Set the stop button image too.
		self.wTree.get_object("btnStop").set_image(Gtk.Image.new_from_icon_name('gtk-media-stop', size))
		# And the next one.
		self.wTree.get_object("btnNext").set_image(Gtk.Image.new_from_icon_name('gtk-media-next', size))
		# Restart one too.
		self.wTree.get_object("btnRestart").set_image(Gtk.Image.new_from_icon_name('gtk-media-previous', size))
		
	
	
	def createPlayTimers(self):
		# Destroy the timers first to avoid about 20 of them.
		self.destroyPlayTimers()
		# Create timers that go off every minute, and second.
		self.tmrSec = GLib.timeout_add_seconds(1, self.secondTimer)
		self.tmrMin = GLib.timeout_add_seconds(60, self.minuteTimer)
	
	def destroyPlayTimers(self):
		# Destroy the timers since nothing's happening.
		if self.tmrMin: GLib.source_remove(self.tmrMin)
		if self.tmrSec: GLib.source_remove(self.tmrSec)

	
	def fsActive(self):
		## Returns True if fullscreen is active.
		return self.mainWindow.get_property('window').get_state() & Gdk.WindowState.FULLSCREEN
		
	
	def showOpenDialogue(self, widget=None):
		## Shows the open file dialogue.
		# Prepare the dialogue.
		dlg = dialogues.OpenFile(self.mainWindow, useful.lastFolder, allowSub=True)

		if (dlg.files):
			# If the response is OK, play the first file, then queue the others.
			# Clear the queue first though, since it is now obsolete.
			queue.clear()
			# Set the last folder, (if it exists).
			if (dlg.dir): useful.lastFolder = dlg.dir
			
			if dlg.chkSubs.get_property('active'):
				# If the user want's subtitles, let them choose the stream.
				dlg2 = dialogues.OpenFile(self.mainWindow, useful.lastFolder, multiple=False, useFilter=False, title=_("Choose a Subtitle Stream"))
				if dlg2.files:
					player.player.set_property('suburi', useful.filenameToUri(dlg2.files[0]))
					player.player.set_property('subtitle-encoding', cfg.getStr('video/subenc'))
				else:
					# Bail if they chose add subtitles but then clicked cancel.
					return
			
			# Play the first file and append the rest to the queue.
			self.playFile(dlg.files[0])
			queue.appendMany(dlg.files[1:])

	
	
	def showAboutDialogue(self, widget):
		dialogues.AboutDialogue(self.mainWindow)
	
	
	def showPreferencesDialogue(self, widget):
		preferences.Dialogue(self, self.mainWindow)
	
	def showPlayDVDDialogue(self, widget):
		# Create the dialogue.
		dlg = dialogues.PlayDVD(self.mainWindow)
		if (dlg.res):
			self.playDVD(dlg.Title)
	
	def showOpenURIDialogue(self, widget):
		# Create and get the dialogue.
		dlg = dialogues.OpenURI(self.mainWindow)
		if (dlg.res):
			# If something was input, play it.
			self.playFile(dlg.URI)
	
	def showAudioTracksDialogue(self, widget):
		# Show the audio track selection dialogue (hopefully will handle subtitles too soon).
		dialogues.SelectAudioTrack(self.mainWindow, self.audioTracks)
	
	def openSubtitleManager(self, widget):
		# Shows the subtitle manager.
		manager = subtitles.subMan(self.mainWindow)
	
	def toggleQueueWindow(self, widget=None, event=None):
		if (widget is self.wTree.get_object('mnuiQueue')):
			# If the call is from the menu item use its tick box value.
			toShow = widget.get_property('active')
			queue.toggle(toShow)
		else:
			# Otherwise just toggle it.
			toShow = queue.toggle()
		
		# Grow/Shrink the window if we're Opening/Closing the queue.
		if (toShow):
			useful.modifyWinHeight(self.mainWindow, queue.queueHeight)
		else:
			useful.modifyWinHeight(self.mainWindow, - (queue.queueHeight))
	
	def toggleAdvControls(self, widget=None):
		## Toggles the advanced controls.
		# Get the menu item's state so we know to show or hide.
		toShow = widget.get_property('active')
		# Get the hbox, then show or hide it accordingly.
		ctrls = self.wTree.get_object("hboxAdvCtrls")
		if (toShow):
			ctrls.show()
			#hboxHeight = ctrls.get_allocation().height
			#useful.modifyWinHeight(self.mainWindow, hboxHeight)
		else:
			ctrls.hide()
			# If we're closing it, we should shrink the main window too.
			#hboxHeight = ctrls.get_allocation().height
			#useful.modifyWinHeight(self.mainWindow, - (hboxHeight))
	
	def connectLinkHooks(self):
		## Make hooks for opening URLs and e-mails.
		if (useful.checkLinkHandler):
			#FIXME gt transition.
			#gtk.about_dialog_set_email_hook(self.URLorMailOpen, 'mail')
			#gtk.about_dialog_set_url_hook(self.URLorMailOpen, 'url')
			pass
		else:
			# xdg-open doesn't exist.
			print _("%s not found, links & e-mail addresses will not be clickable" % useful.linkHandler)
	
	def URLorMailOpen(self, dialog, link, type):
		# Transfers the call to the useful call.
		useful.URLorMailOpen(link, type)
	
	def openBugReporter(self, widget):
		## Opens the bugs webpage.
		link = "http://gna.org/bugs/?group=whaawmp"
		if (useful.checkLinkHandler):
			useful.URLorMailOpen(link)
		else:
			dialogues.ErrorMsgBox(self.mainWindow, _("Could not execute browser command (via %(program)s).\nPlease manually visit %(url)s to report the problem" % {'program' : useful.linkHandler, 'url' : link}))
	
	# Just a transfer call as player.stop takes only 1 argument.
	stopPlayer = lambda self, widget: player.stop()
	
	def sigterm(self,num,frame):
		# Quit when sigterm signal caught.
		print _("TERM signal caught, exiting.")
		self.quit()
	
	def openSupFeaturesDlg(self, widget):
		# Shows the supported features dialogue.
		dialogues.SupportedFeatures(self.mainWindow)
	
	def onPlaySpeedChange(self, widget):
		# Changes the players current speed.
		player.changeSpeed(widget.get_value())
	
	def numQueuedChanged(self, queued):
		# Called when the number of files queued changes.
		label = self.wTree.get_object('lblNumQueued')
		sep = self.wTree.get_object('vsepQueued') # (The seperator)
		# Only show the queued label if the queue is non empty.
		for x in [label, sep]:
			if (queued > 0):
				x.show()
			else:
				x.hide()
		# Set the label according to the queue length.
		label.set_label(_("Queued: %d") % queued)
	
	
	def __init__(self):
		# Set the last folder to the directory from which the program was called.
		useful.lastFolder = useful.origDir
		# Set the application's name (for about dialogue etc).
		GLib.set_application_name(str(useful.lName))
		
		# Create & prepare the player for playing.
		self.preparePlayer()
		# Connect up the sigterm signal.
		signal.signal(signal.SIGTERM, self.sigterm)
		
		if msgBus.avail: self.dbus = msgBus.IntObject(self)
		
		# Set up the gtk-builder and interface.
		self.wTree = Gtk.Builder()
		windowname = "main"
		self.wTree.add_from_file(useful.getBuilderFile('main'))
		
		dic = { "on_main_delete_event" : self.quit,
		        "on_mnuiQuit_activate" : self.quit,
		        "on_mnuiOpen_activate" : self.showOpenDialogue,
		        "on_mnuiOpenURI_activate" : self.showOpenURIDialogue,
		        "on_btnPlayToggle_clicked" : self.togglePlayPause,
		        "on_btnStop_clicked" : self.stopPlayer,
		        "on_btnNext_clicked" : self._cb_on_btnNext_clicked,
		        "on_btnRestart_clicked" : self.restartTrack,
		        "on_pbarProgress_button_press_event" : self.progressBarClick,
		        "on_pbarProgress_button_release_event" : self.seekEnd,
		        "on_pbarProgress_motion_notify_event" : self.progressBarMotion,
		        "on_pbarProgress_change_value" : self.seekFromProgress,
		        "on_btnVolume_value_changed" : self.changeVolume,
		        "on_mnuiFS_activate" : self.toggleFullscreen,
		        "on_btnLeaveFullscreen_clicked" : self.toggleFullscreen,
		        "on_videoWindow_draw" : self.videoWindowDraw,
		        "on_videoWindow_configure_event" : self.videoWindowConfigure,
		        "on_main_key_press_event" : self.windowKeyPressed,
		        "on_videoWindow_button_press_event" : self.videoWindowClicked,
		        "on_videoWindow_scroll_event" : self.videoWindowScroll,
		        "on_mnuiAbout_activate" : self.showAboutDialogue,
		        "on_main_drag_data_received" : self.openDroppedFiles,
		        "on_videoWindow_motion_notify_event" : self.videoWindowMotion,
		        "on_videoWindow_leave_notify_event" : self.videoWindowLeave,
		        "on_videoWindow_enter_notify_event" : self.videoWindowEnter,
		        "on_mnuiPreferences_activate" : self.showPreferencesDialogue,
		        "on_mnuiPlayDVD_activate" : self.showPlayDVDDialogue,
				"on_mnuiDVDMenu_activate" : self.gotoDVDMenu,
		        "on_mnuiAudioTrack_activate" : self.showAudioTracksDialogue,
				"on_mnuiSubtitleManager_activate" : self.openSubtitleManager,
		        "on_mnuiReportBug_activate" : self.openBugReporter,
		        "on_main_window_state_event" : self.onMainStateEvent,
		        "on_mnuiQueue_toggled" : self.toggleQueueWindow,
		        "on_eventNumQueued_button_release_event" : self.toggleQueueWindow,
		        "on_mnuiAdvCtrls_toggled" : self.toggleAdvControls,
		        "on_mnuiSupFeatures_activate" : self.openSupFeaturesDlg,
		        "on_spnPlaySpeed_value_changed" : self.onPlaySpeedChange }
		self.wTree.connect_signals(dic)
		
		# Add the queue to the queue box.
		self.wTree.get_object("queueBox").pack_start(queue.qwin, True, True, 0)
		
		# Get several items for access later.
		useful.mainWin = self.mainWindow = self.wTree.get_object(windowname)
		self.progressBar = self.wTree.get_object("pbarProgress")
		self.lblElapsed = self.wTree.get_object("lblElapsed")
		self.lblDuration = self.wTree.get_object("lblDuration")
		self.videoWindow = self.wTree.get_object("videoWindow")
		self.nowPlyLbl = self.wTree.get_object("lblNowPlaying")
		self.volAdj = self.wTree.get_object("btnVolume").get_adjustment()
		self.hboxVideo = self.wTree.get_object("hboxVideo")
		queue.mnuiWidget = self.wTree.get_object("mnuiQueue")
		# Set gapless flag
		self.isvideo = None
		# Set the icon.
		self.mainWindow.set_icon_from_file(os.path.join(useful.dataDir, 'images', 'whaawmp48.png'))
		# Set the window to allow drops
		# FIXME gi transition.
		#self.mainWindow.drag_dest_set(Gtk.DestDefaults.ALL, [("text/uri-list", 0, 0)], Gdk.DragAction.COPY)
		# If we drop stuff on the queue label we want it queued (bottom right)
		# FIXME gi transition.
		#self.wTree.get_object('lblNumQueued').drag_dest_set(Gtk.DestDefaults.ALL, [("text/uri-list", 0, 0)], Gdk.DragAction.COPY)
		self.wTree.get_object('lblNumQueued').connect('drag-data-received', queue.enqueueDropped)
		# Update the progress bar.
		#self.progressUpdate()
		# Get the volume from the configuration.
		volVal = cfg.getFloat("audio/volume") if (cfg.cl.volume == None) else float(cfg.cl.volume)
		self.volAdj.set_value(useful.toRange(volVal, 0, 1))
		# Set the quit on stop checkbox.
		self.wTree.get_object("mnuiQuitOnStop").set_property('active', cfg.cl.quitOnEnd)
		# Set up the default flags.
		self.controlsShown = True
		self.seeking = False
		# Call the function to change the play/pause image.
		self.playPauseChange(False)
		# Show the next button & restart track button if enabled.
		if (cfg.getBool("gui/shownextbutton")): self.wTree.get_object("btnNext").show()
		if (cfg.getBool("gui/showrestartbutton")): self.wTree.get_object("btnRestart").show()
		# Setup the signals.
		signals.connect('toggle-play-pause', self.togglePlayPause)
		signals.connect('toggle-fullscreen', self.toggleFullscreen)
		signals.connect('play-next', self.playNext, False)
		signals.connect('restart-track', self.restartTrack)
		signals.connect('toggle-queue', queue.toggle)
		signals.connect('toggle-advanced-controls', self.toggleAdvancedControls)
		signals.connect('queue-changed', self.numQueuedChanged)
		# Show the window.
		self.mainWindow.show()
		# Save the windows ID so we can use it to inhibit screensaver.
		useful.winID = self.mainWindow.get_property('window').get_xid()
		self.vidxid = self.videoWindow.get_property('window').get_xid()
		# Set the queue play command, so it can play tracks.
		queue.playCommand = self.playFile
		# Play a file (if it was specified on the command line).
		if (len(cfg.args) > 0):
			# Append all tracks to the queue.
			queue.appendMany(cfg.args)
			# Then play the next track.
			GLib.idle_add(self.playNext, False)
		
		if (cfg.cl.fullscreen):
			# If the fullscreen option was passed, start fullscreen.
			self.activateFullscreen()
		
		# Connect the hooks.
		self.connectLinkHooks()
		
		# Enter the GTK main loop.
		Gtk.main()
