#!/usr/bin/env python

#  Whaaw! Media Player main window.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
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

import sys, os, os.path, urllib
import pygtk
pygtk.require('2.0')
import gtk, gobject
gobject.threads_init()
import gtk.glade

from common import gstPlayer as player
from gui import dialogues
from common import lists, useful
from common import gstTools as playerTools

class mainWindow:
	def quit(self, widget=None, event=None):
		## Quits the program.
		# Stop the player first to avoid tracebacks.
		self.player.stop()
		# Save the configuration to the file.
		self.cfg.save()
		gtk.main_quit()
	
	
	def videoWindowExpose(self, widget, event):
		# Pull the dimensions etc.
		x, y, w, h = event.area
		
		# Let the whole thing be drawn upon.
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.pixmap, x, y, x, y, w, h)
		
		# If we're not playing, draw the backing image.
		if (not self.player.playingVideo()): self.movieWindowOnStop()
	
	
	def videoWindowConfigure(self, widget, event=None):
		# Get the windows allocation.
		x, y, w, h = widget.get_allocation()
		
		# Make a new pixmap (does this create a leak?)
		self.pixmap = gtk.gdk.Pixmap(widget.window, w, h)
		
		# Fill the whole thing with black so it looks nicer (better than white).
		self.pixmap.draw_rectangle(widget.get_style().black_gc, True, 0, 0, w, h)
		# Queue the drawing area.
		widget.queue_draw()
	
	
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
			gobject.source_remove(self.idleTimer)
		except:
			pass
	
	def createIdleTimer(self):
		# Create the timer again, with the timeout reset.
		self.idleTimer = gobject.timeout_add(self.cfg.getInt("gui/mousehidetimeout"), self.hideControls)
	
	
	def showControls(self):
		## Shows the fullscreen controls (also the mouse):
		# Re show the cursor.
		self.setCursor(None, self.movieWindow)
		# Shows all the widgets that should be shown.
		if (not self.controlsShown):
			# If the controls aren't shown, show them.
			for x in lists.fsShowWMouse:
				self.wTree.get_widget(x).show()
			# Flag the controls as being shown.
			self.controlsShown = True
	
	
	def hideControls(self):
		## Hides the fullscreen controls (also the mouse).
		# We don't want anything hidden if no video is playing.
		if (not self.player.playingVideo()): return
		# Hide the cursor.
		self.hideCursor(self.movieWindow)
		if (self.fsActive()):
			# Only hide the controls if we're in fullscreen.
			# Hides all the widgets that should be hidden.
			for x in lists.fsShowWMouse:
				self.wTree.get_widget(x).hide()
			# Flag the controls as being hidden.
			self.controlsShown = False
	
	
	def hideCursor(self, widget):
		## Hides the cursor (Thanks to mirage for the code).
		# If there's no video playing, cancel it.
		if (not self.player.playingVideo()): return
		pix_data = """/* XPM */
			static char * invisible_xpm[] = {
			"1 1 1 1",
			"       c None",
			" "};"""
		colour = gtk.gdk.Color()
		pix = gtk.gdk.pixmap_create_from_data(None, pix_data, 1, 1, 1, colour, colour)
		invisible = gtk.gdk.Cursor(pix, pix, colour, colour, 0, 0)
		# Set the cursor to the one just created.
		self.setCursor(invisible, widget)
	
	def setCursor(self, mode, widget):
		## Sets a cursor to the one specified.
		widget.window.set_cursor(mode)
	
	
	def activateFullscreen(self, widget=None):
		## Activates fullscreen.
		# No use in doing fullscreen if no video is playing.
		if (not self.player.playingVideo()): return
		
		# Set the window to fullscreen.
		self.mainWindow.fullscreen()

	
	def deactivateFullscreen(self):
		## Deactivates the fullscreen.
		# Hide all the widgets, before we unfullscreen.
		for x in lists.hiddenFSWidgets:
			self.wTree.get_widget(x).hide()
		# Unfullscreens the window (in 100ms so the window is the right size
		# (is there a better way of doing this?).
		gobject.timeout_add(100, self.mainWindow.unfullscreen)
	
	
	def toggleFullscreen(self, widget=None):
		# If the fullscreen window is shown, hide it, otherwise, show it.
		if (self.fsActive()):
			self.deactivateFullscreen()
		else:
			self.activateFullscreen()
	
	
	def setImageSink(self, widget=None):
		## Sets the image sink to 'widget' or whichever it discovers.
		if (not widget):
			# If no widget was passed, use the right one. (This is left from
			# when I had a separate fullscreen window, maybe it should be fixed?)
			widget = self.movieWindow
		
		# Configure the video area.
		self.videoWindowConfigure(widget)
		
		# Set the image sink accordingly.
		self.player.setImgSink(widget)
		
		return False
	
	
	def videoWindowClicked(self, widget, event):
		# Get the even information.
		x, y, state = event.window.get_pointer()
		
		if (event.type == gtk.gdk._2BUTTON_PRESS and state & gtk.gdk.BUTTON1_MASK):
			# If the window was double clicked, fullsreen toggle.
			self.toggleFullscreen()
		elif (event.type == gtk.gdk.BUTTON_PRESS and state & gtk.gdk.BUTTON2_MASK):
			# If it was middle clicked, toggle play/pause.
			self.togglePlayPause()

	
	def videoWindowScroll(self, widget, event):
		## Changes the volume on scroll up/down.
		if (event.direction == gtk.gdk.SCROLL_UP):
			self.increaseVolumeBy(self.cfg.getFloat('gui/volumescrollchange'))
		elif (event.direction == gtk.gdk.SCROLL_DOWN):
			self.increaseVolumeBy(0 - self.cfg.getFloat('gui/volumescrollchange'))
	
	
	def increaseVolumeBy(self, change):
		## Increases the volume by the amount given.
		val = self.volAdj.value + change
		# Make sure the new value is withing the bounds (0 <= val <= 100)
		val = useful.toRange(val, 0, 100)
		# Adjust the volume.
		self.volAdj.value = val
	
	
	def windowKeyPressed(self, widget, event):
		## I should probably make the bindings customisable (event.keyval
		# for that probably).
		if (event.string == ' '):
			# Toggle Play/Pause on Spacebar.
			self.togglePlayPause()
		elif (event.string == 'f'):
			# Toggle fullscreen on 'f'.
			self.toggleFullscreen()

	
	def preparePlayer(self):
		## This prepares the player.
		# Create a new player.
		self.player = player.player()
		# Get the bus and connect the signals.
		bus = self.player.getBus()
		bus.connect('message', self.onPlayerMessage)
		bus.connect('sync-message::element', self.onPlayerSyncMessage)
		# Sets the sinks to that in the config (unless one was specified at launch).
		asink = self.cfg.getStr("audio/audiosink") if (not self.options.audiosink) else self.options.audiosink
		self.player.setAudioSink(None if (asink == "default") else asink)
		vsink = self.cfg.getStr("video/videosink") if (not self.options.videosink) else self.options.videosink
		self.player.setVideoSink(playerTools.vsinkDef() if (vsink == "default") else vsink)
	
	
	def onPlayerMessage(self, bus, message):
		t = playerTools.messageType(message)
		if (t == 'eos'):
			# At the end of a stream, stop the player.
			self.player.stop()
		elif (t == 'error'):
			# On an error, empty the currently playing file (also stops it).
			self.playFile(None)
			# Show an error about the failure.
			msg = message.parse_error()
			dialogues.ErrorMsgBox(self.mainWindow, str(msg[0]) + '\n\n' + str(msg[1]), _('Error!'))
		elif (t == 'state_changed' and message.src == self.player.player):
			self.onPlayerStateChange(message)
	
	
	def onPlayerStateChange(self, message):
		# On a state change.
		msg = message.parse_state_changed()
		if (playerTools.isNull2ReadyMsg(msg)):
			# Enable the visualisation if requested.
			if (self.cfg.getBool('gui/enablevisualisation')):
				self.player.enableVisualisation()
			else:
				self.player.disableVisualisation()
		
		elif (playerTools.isStop2PauseMsg(msg)):
			# The player has gone from stopped to paused.
			# Get the array of audio tracks.
			self.audioTracks = playerTools.getAudioLangArray(self.player)
			# Only enable the audio track menu item if there's more than one audio track.
			self.wTree.get_widget('mnuiAudioTrack').set_sensitive(len(self.audioTracks) > 1)
			if (playerTools.hasVideoTrack(self.player) or self.cfg.getBool('gui/enablevisualisation')):
				# Show the video window if the stream has a video track (or visualisations).
				self.showVideoWindow()
				# Also enable the Toggle Fullscreen menuitem.
				self.wTree.get_widget('mnuiFS').set_sensitive(True)
			# Enable the visualisation if requested.
			if (self.cfg.getBool('gui/enablevisualisation')):
				self.player.enableVisualisation()
			else:
				self.player.disableVisualisation()
		
		elif (playerTools.isPlayMsg(msg)):
			# The player has just started.
			# Set the play/pause image to pause.
			self.playPauseChange(True)
			# Create the timers.
			self.createPlayTimers()
			
		elif (playerTools.isPlay2PauseMsg(msg)):
			# It's just been paused or stopped.
			self.playPauseChange(False)
			# Destroy the play timers.
			self.destroyPlayTimers()
			# Update the progress bar.
			self.progressUpdate()
			
		elif (playerTools.isStopMsg(msg)):
			if (self.wTree.get_widget("mnuiQuitOnStop").get_active()): self.quit()
			# Draw the background image.
			self.movieWindowOnStop()
			# Deactivate fullscreen.
			if (self.fsActive()): self.deactivateFullscreen()
			# Disable the Toggle Fullscreen menuitem.
			self.wTree.get_widget('mnuiFS').set_sensitive(False)
			# Reset the progress bar.
			self.progressUpdate()
	
	
	def onPlayerSyncMessage(self, bus, message):
		if (message.structure is None):
			return
		
		if (message.structure.get_name() == 'prepare-xwindow-id'):
			# If it's playing a video, set the video properties.
			# Get the properties of the video.(Brightness etc)
			far = self.cfg.getBool("video/force-aspect-ratio")
			b = self.cfg.getInt("video/brightness")
			c = self.cfg.getInt("video/contrast")
			h = self.cfg.getInt("video/hue")
			s = self.cfg.getInt("video/saturation")
			self.player.prepareImgSink(bus, message, far, b, c, h, s)
			# Set the image sink to whichever viewer is active.
			self.setImageSink()
				
	
	def openDroppedFile(self, widget, context, x, y, selection_data, info, time):
		## Opens a file after a drag and drop.
		# Split all the files that were input.
		uris = selection_data.data.strip().split()
		# Can only play one file at once, so use the first one.
		uri = urllib.url2pathname(uris[0])
		
		# Actually play the file.
		self.playFile(uri)
		# Finish the drag.
		context.finish(True, False, time)
	
	
	def playFile(self, file):
		## Plays the file 'file' (Could also be a URI).
		# First, stop the player.
		self.player.stop()
		# Set the audio track to 0
		self.player.setAudioTrack(0)
		
		if (file == None):
			# If no file is to be played, set the URI to None, and the file to ""
			file = ""
			self.player.setURI(file)
		# Set the now playing label to the file to be played.
		self.nowPlyLbl.set_label("" + file)
		if (os.path.exists(file) or '://' in file):
			# If it's not already a uri, make it one.
			if ('://' not in file): file = 'file://' + file
			# Set the URI to the file's one.
			self.player.setURI(file)
			# Start the player.
			self.player.play()
		elif (file != ""):
			# If none of the above, a bad filename was passed.
			print _("Something's stuffed up, no such file: %s") % (file)
			self.playFile(None)
	
	
	def playDVD(self, title=None):
		## Plays a DVD
		# Start the player playing the DVD.
		self.playFile('dvd://%s' % (title if (title != None) else ""))
			
	
	def togglePlayPause(self, widget=None):
		## Toggles the player play/pause.
		
		if (not self.player.getURI()):
			# If there is no currently playing track, we should show the
			# open file dialogue.
			self.showOpenDialogue()
			return
		
		if (self.player.isPlaying()):
			# If the player is playing, pause the player.
			self.player.pause()
		else:
			# If it's already paused (or stopped with a file): play.
			self.player.play()
	
	
	def minuteTimer(self):
		## A timer that runs every minute while playing.
		# Disable XScreenSaver (if option is enabled).
		if (self.cfg.getBool("misc/disablexscreensaver") and self.player.playingVideo()):
			os.system("xscreensaver-command -deactivate >&- 2>&-")
			os.system("xset s reset >&- 2>&-")
		
		return self.player.isPlaying()
	
	
	def secondTimer(self):
		# A function that's called once a second while playing.
		if (not self.seeking): self.progressUpdate()
		
		# Causes it to go again if it's playing, but stop if it's not.
		return self.player.isPlaying()
		
	
	def progressUpdate(self, pld=None, tot=None):
		## Updates the progress bar.
		if (self.player.isStopped()):
			# If the player is stopped, played time and total should 
			# be 0, and the progress should be 0.
			pld = tot = 0
			self.progressBar.set_fraction(0)
		else:
			# Otherwise (playing or paused), get the track time data, set
			# the progress bar fraction.
			if (pld == None or tot == None): pld, tot = self.player.getTimesSec()
			if (tot > 0): self.progressBar.set_fraction(pld / tot)
		
		# Convert played & total time to integers
		p, t = int(pld), int(tot)
		# Add the data to the progress bar's text.
		text = ""
		text += useful.secToStr(p)
		if (tot > 0):
			text += " / "
			text += useful.secToStr(t - (self.cfg.getBool('gui/showtimeremaining') * p))
		self.progressBar.set_text(text)
	
	
	def onMainStateEvent(self, widget, event):
		## Acts when a state event occurs on the main window.
		fs = event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN
		if (fs):
			# Hide all the widgets other than the video window.
			for x in lists.hiddenFSWidgets:
				self.wTree.get_widget(x).hide()
			
			# Flag the the controls as not being shown.
			self.controlsShown = False
		else:
			# Re-show all the widgets that aren't meant to be hidden.
			for x in lists.hiddenFSWidgets:
				if (x not in lists.hiddenNormalWidgets): self.wTree.get_widget(x).show()
			# Flag the controls as being shown.
			self.controlsShown = True
		
		if (not fs and not self.player.playingVideo()):
			# If fullscreen is not active and no video is playing, call the
			# movie stop function in 0ms (for some reason this seems to work).
			gobject.timeout_add(0, self.movieWindowOnStop, True)
	
	
	def showVideoWindow(self):
		## Shows the video window.
		# Set the packing type of the video window to expand.
		self.hboxVideo.set_child_packing(self.movieWindow, True, True, 0, 'start')
		# Set the video window's size too.
		self.movieWindow.set_size_request(480, 360)
	
	def hideVideoWindow(self, force=False):
		## Hides the video window.
		if (not self.fsActive() and (self.movieWindow.get_size_request() != (-1, -1) or force)):
			# Set the packing type of the video window to not.
			self.hboxVideo.set_child_packing(self.movieWindow, False, True, 0, 'start')
			# Set the video window's size to small.
			self.movieWindow.set_size_request(-1, -1)
			# Make the height of the window as small as possible.
			w = self.mainWindow.get_size()[0]
			self.mainWindow.resize(w, 1)
		
	
	def seekStart(self, widget, event):
		## Sets that seeking has started.
		x, y, state = event.window.get_pointer()
		if (state & gtk.gdk.BUTTON1_MASK and not self.player.isStopped() and self.player.getDuration()):
			# If it's button 1, it's not stopped and the duration exists: start seeking.
			self.seeking = True
			
			self.progressBarMotion(widget, event)
	
	
	def seekEnd(self, widget, event):
		## Sets that seeking has ended, and seeks to the position.
		if (self.seeking):
			self.seekFromProgress(widget, event)
			# Flag that seeking has stopped.
			self.seeking = False
	
	
	def seekFromProgress(self, widget, event):
		x, y, state = event.window.get_pointer()
		# Get the width of the bar.
		maxX = widget.get_allocation().width
		# Seek to the location.
		self.player.seekFrac(float(x) / maxX)
		# Update the progress bar to reflect the change.
		self.progressUpdate()
		
		
	def progressBarMotion(self, widget, event):
		## when the mouse moves over the progress bar.
		# If we're not seeking, cancel.
		if (not self.seeking): return
		# Check if the mouse button is still down, just in case we missed it.
		x, y, state = event.window.get_pointer()
		if (not state & gtk.gdk.BUTTON1_MASK): self.seekEnd(widget, event)
		if (self.cfg.getBool("gui/instantseek")):
			# If instantaneous seek is set, seek!
			self.seekFromProgress(widget, event)
			return
		
		# Get the mouse co-ordinates, the width of the bar and the file duration.
		x, y = event.get_coords()
		maxX = widget.get_allocation().width
		dur = self.player.getDurationSec()
		# Convert the information to a fraction, and make sure 0 <= frac <= 1
		frac = useful.toRange(float(x) / maxX, 0, 1)
		
		# Set the progress bar to the new data.
		self.progressUpdate((frac * dur), dur)
		
	
	def volumeButtonToggled(self, widget):
		## Toggles Mute
		self.player.setVolume(self.volAdj.value if (widget.get_active()) else 0)
		# Save the mutedness in the config.
		self.cfg.set("audio/mute", not widget.get_active())
		
	def changeVolume(self, widget):
		## Change the volume to that indicated by the volume bar.
		vol = widget.get_value()
		self.player.setVolume(vol if (not self.cfg.getBool("audio/mute")) else 0)
		# Set the new volume on the configuration.
		self.cfg.set("audio/volume", vol)
	
	
	def playPauseChange(self, playing):
		## Changes the play/pause image according to the argument.
		# Set the size.
		size = self.cfg.getInt("gui/iconsize")
		# Set the icon accordingly (Not playing -> Pause button, otherwise, play.)
		img = gtk.image_new_from_stock('gtk-media-play' if (not playing) else 'gtk-media-pause', size)
		
		btn = self.wTree.get_widget("btnPlayToggle")
		# Actually set the icon.
		btn.set_image(img)
		# Also set the tooltip.
		self.tooltips.set_tip(btn, _('Pause') if (playing) else _('Play'))
		# Set the stop button image too.
		self.wTree.get_widget("btnStop").set_image(gtk.image_new_from_stock('gtk-media-stop', size))
	
	
	def createPlayTimers(self):
		# Destroy the timers first to avoid about 20 of them.
		self.destroyPlayTimers()
		# Create timers that go off every minute, and second.
		self.tmrSec = gobject.timeout_add(1000, self.secondTimer)
		self.tmrMin = gobject.timeout_add(60000, self.minuteTimer)
	
	def destroyPlayTimers(self):
		# Destroy the timers since nothing's happening.
		try:
			gobject.source_remove(self.tmrMin)
			gobject.source_remove(self.tmrSec)
		except:
			pass
	
	
	def movieWindowOnStop(self, force=False):
		## Called when the player stops, acts on the movie window.
		if (self.cfg.getBool("gui/hidevideowindow")):
			# If the video window should be hidden, hide it, otherwise, draw the picture.
			self.hideVideoWindow(force)
		else:
			self.showVideoWindow()
			self.drawMovieWindowImage()
	
	
	def drawMovieWindowImage(self):
		## Draws the background image.
		# Just return until we actually have a picture to display.
		return
		try:
			# Try and draw the image.
			self.movieWindow.window.draw_pixbuf(self.movieWindow.get_style().black_gc, self.bgPixbuf, 0, 0, 0, 0)
		except:
			# If that fails, we need to get the image from the file.
			# Get the image file.
			image = os.path.join(useful.srcDir, '..', 'images', 'whaawmp.png')
			# Create a pixbuf from the file.
			self.bgPixbuf = gtk.gdk.pixbuf_new_from_file(image)
			# Draw the image on the file.
			self.movieWindow.window.draw_pixbuf(self.movieWindow.get_style().black_gc, self.bgPixbuf, 0, 0, 0, 0)

	
	def fsActive(self):
		## Returns True if fullscreen is active.
		return self.mainWindow.window.get_state() & gtk.gdk.WINDOW_STATE_FULLSCREEN
		
	
	def showOpenDialogue(self, widget=None):
		## Shows the open file dialogue.
		# Prepare the dialogue.
		dlg = dialogues.OpenFile(self.mainWindow, self.lastFolder)

		if (dlg.file):
			# If the response is OK, play the file.		
			self.playFile(dlg.file)
			# Also set the last folder.
			self.lastFolder = dlg.dir
	
	
	def showAboutDialogue(self, widget):
		dialogues.AboutDialogue(self.mainWindow)
	
	
	def showPreferencesDialogue(self, widget):
		dialogues.PreferencesDialogue(self, self.mainWindow)
	
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
		# Show the audio track selection dialogue (hopefully will handle subtitles too soon.
		dialogues.SelectAudioTrack(self.mainWindow, self.audioTracks, self.player)
	
	# Just a transfer call as player.stop takes only 1 argument.
	stopPlayer = lambda self, widget: self.player.stop()
	
	
	def __init__(self, main, options, args):
		# Set the last folder to the directory from which the program was called.
		self.cfg = main.cfg
		self.options = options
		self.lastFolder = useful.origDir
		
		# Create & prepare the player for playing.
		self.preparePlayer()
		
		windowname = "main"
		self.wTree = gtk.glade.XML(useful.gladefile, windowname, useful.sName)
		
		dic = { "on_main_delete_event" : self.quit,
		        "on_mnuiQuit_activate" : self.quit,
		        "on_mnuiOpen_activate" : self.showOpenDialogue,
		        "on_mnuiOpenURI_activate" : self.showOpenURIDialogue,
		        "on_btnPlayToggle_clicked" : self.togglePlayPause,
		        "on_btnStop_clicked" : self.stopPlayer,
		        "on_pbarProgress_button_press_event" : self.seekStart,
		        "on_pbarProgress_button_release_event" : self.seekEnd,
		        "on_pbarProgress_motion_notify_event" : self.progressBarMotion,
		        "on_chkVol_toggled" : self.volumeButtonToggled,
		        "on_hscVolume_value_changed" : self.changeVolume,
		        "on_mnuiFS_activate" : self.toggleFullscreen,
		        "on_btnLeaveFullscreen_clicked" : self.toggleFullscreen,
		        "on_videoWindow_expose_event" : self.videoWindowExpose,
		        "on_videoWindow_configure_event" : self.videoWindowConfigure,
		        "on_main_key_press_event" : self.windowKeyPressed,
		        "on_videoWindow_button_press_event" : self.videoWindowClicked,
		        "on_videoWindow_scroll_event" : self.videoWindowScroll,
		        "on_hscVolume_scroll_event" : self.videoWindowScroll,
		        "on_mnuiAbout_activate" : self.showAboutDialogue,
		        "on_main_drag_data_received" : self.openDroppedFile,
		        "on_videoWindow_motion_notify_event" : self.videoWindowMotion,
		        "on_videoWindow_leave_notify_event" : self.videoWindowLeave,
		        "on_videoWindow_enter_notify_event" : self.videoWindowEnter,
		        "on_mnuiPreferences_activate" : self.showPreferencesDialogue,
		        "on_mnuiPlayDVD_activate" : self.showPlayDVDDialogue,
		        "on_mnuiAudioTrack_activate" : self.showAudioTracksDialogue,
		        "on_main_window_state_event" : self.onMainStateEvent }
		self.wTree.signal_autoconnect(dic)
		
		# Get several items for access later.
		self.mainWindow = self.wTree.get_widget(windowname)
		self.progressBar = self.wTree.get_widget("pbarProgress")
		self.movieWindow = self.wTree.get_widget("videoWindow")
		self.nowPlyLbl = self.wTree.get_widget("lblNowPlaying")
		self.volAdj = self.wTree.get_widget("hscVolume").get_adjustment()
		self.hboxVideo = self.wTree.get_widget("hboxVideo")
		# Create a tooltips instance for use in the code.
		self.tooltips = gtk.Tooltips()
		# Set the window to allow drops
		self.mainWindow.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY)
		# Update the progress bar.
		self.progressUpdate()
		# Get the volume from the configuration.
		self.wTree.get_widget("chkVol").set_active(not (self.cfg.getBool("audio/mute") or (options.mute)))
		self.volAdj.value = self.cfg.getFloat("audio/volume") if (options.volume == None) else float(options.volume)
		# Set the quit on stop checkbox.
		self.wTree.get_widget("mnuiQuitOnStop").set_active(options.quitOnEnd)
		# Set up the default flags.
		self.controlsShown = True
		self.seeking = False
		# Call the function to change the play/pause image.
		self.playPauseChange(False)
		# Show the window.
		self.mainWindow.show()
		# Play a file (if it was specified on the command line).
		if (len(args) > 0):
			self.playFile(args[0] if ('://' in args[0]) else os.path.abspath(args[0]))
		else:
			self.movieWindowOnStop(True)
		
		#Configure the movie window.
		self.videoWindowConfigure(self.movieWindow)
		if (options.fullscreen):
			# If the fullscreen option was passed, start fullscreen.
			self.activateFullscreen()
		
		# Enter the GTK main loop.
		gtk.main()
