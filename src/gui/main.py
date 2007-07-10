#!/usr/bin/env python

#  Whaaw! Media Player main window.
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

import sys, os, os.path, urllib
import pygtk
pygtk.require('2.0')
import gtk, gobject
gobject.threads_init()
import gtk.glade
import pygst
pygst.require('0.10')
import gst

import gstPlayer as player
from gui import dialogues
import lists
import useful
import gstTools as playerTools

class mainWindow:
	gladefile = "gui" + os.sep + "whaawmp.glade"
	
	def quit(self, widget, event=None):
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
		if (self.player.isStopped()): self.drawMovieWindowImage()
	
	
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
			for x in lists.fsShowWMouse():
				self.wTree.get_widget(x).show()
			# Flag the controls as being shown.
			self.controlsShown = True
	
	
	def hideControls(self):
		## Hides the fullscreen controls (also the mouse).
		# We don't want anything hidden if no video is playing.
		if (not self.player.playingVideo()): return
		# Hide the cursor.
		self.hideCursor(self.movieWindow)
		if (self.fsActive):
			# Only hide the controls if we're in fullscreen.
			# Hides all the widgets that should be hidden.
			for x in lists.fsShowWMouse():
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
		color = gtk.gdk.Color()
		pix = gtk.gdk.pixmap_create_from_data(None, pix_data, 1, 1, 1, color, color)
		invisible = gtk.gdk.Cursor(pix, pix, color, color, 0, 0)
		# Set the cursor to the one just created.
		self.setCursor(invisible, widget)
	
	def setCursor(self, mode, widget):
		## Sets a cursor to the one specified.
		widget.window.set_cursor(mode)
	
	
	def videoActivateFullScreen(self, widget=None):
		## Activates fullscreen.
		# No use in doing fullscreen if no video is playing.
		if (not self.player.playingVideo()): return
		
		# Hide all the widgets other than the video window.
		for x in lists.hiddenFSWidgets():
			self.wTree.get_widget(x).hide()
		
		# Flag the the controls as not being shown.
		self.controlsShown = False
		# Set the window to fullscreen.
		self.mainWindow.fullscreen()
		
		# Flag the fullscreen window as being shown.
		self.fsActive = True

	
	def videoDeactivateFullScreen(self):
		## Deactivates the fullscreen.
		# Unfullscreens the window.
		self.mainWindow.unfullscreen()
		# Re-show all the widgets.
		for x in lists.hiddenFSWidgets():
			self.wTree.get_widget(x).show()
		# Hide any widgets that should be hidden.
		for x in lists.hiddenNormalWidgets():
			self.wTree.get_widget(x).hide()
		# Flag the controls as being shown.
		self.controlsShown = True
		# Unflag the fullscreen window.
		self.fsActive = False
	
	
	def toggleFullScreen(self, widget=None):
		# If the fullscreen window is shown, hide it, otherwise, show it.
		if (self.fsActive):
			self.videoDeactivateFullScreen()
		else:
			self.videoActivateFullScreen()
	
	
	def setImageSink(self, widget=None):
		## Sets the image sink to 'widget' or whichever it discovers.
		## For some reason it I pass the widgets from other functions
		## to here the program likes to crash.
		if (not widget):
			# If no widget was passed, discover which it should use.
			widget = self.fsVideoWin if (self.fsActive) else self.movieWindow
		
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
			self.toggleFullScreen()
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
		if (val > 100): val = 100
		if (val < 0): val = 0
		# Adjust the volume.
		self.volAdj.value = val
	
	
	def windowKeyPressed(self, widget, event):
		## Doesn't work well with compiz, and I should probably make the
		#  bindings customisable (event.keyval for that probably).
		if (event.string == ' '):
			# Toggle Play/Pause on Spacebar.
			self.togglePlayPause()
		elif (event.string == 'f'):
			# Toggle fullscreen on 'f'.
			self.toggleFullScreen()

	
	def preparePlayer(self):
		## This prepares the player.
		# Create a new player.
		self.player = player.player()
		# Get the bus and connect the signals.
		bus = self.player.getBus()
		bus.connect('message', self.onPlayerMessage)
		bus.connect('sync-message::element', self.onPlayerSyncMessage)
		# Sets the sinks.
		asink = self.cfg.getStr("audio/audiosink")
		self.player.setAudioSink(None if (asink == "default") else asink)
		vsink = self.cfg.getStr("video/videosink")
		self.player.setVideoSink(None if (vsink == "default") else vsink)
	
	
	def onPlayerMessage(self, bus, message):
		t = message.type
		if (t == gst.MESSAGE_EOS):
			# At the end of a stream, stop the player.
			self.player.stop()
		elif (t == gst.MESSAGE_ERROR):
			# On an error, empty the currently playing file (also stops it).
			self.playFile(None)
			# Show an error about the failure.
			msg = message.parse_error()
			dialogues.MsgBox(self.mainWindow, str(msg[0]) + '\n\n' + str(msg[1]), _('Error!'))
		elif (message.type == gst.MESSAGE_STATE_CHANGED):
			self.onPlayerStateChange(message)
	
	
	def onPlayerStateChange(self, message):
		# On a state change.
		msg = message.parse_state_changed()
		if (playerTools.isPlayMsg(msg)):
			# The player has started.
			self.audioTracks = []
			for x in self.player.getStreamsInfo():
				# For all streams in the file.
				# Get its type.
				type = playerTools.streamType(x)
				# If it's an audio stream, add it to the array.
				if (type == 'audio'): self.audioTracks.append(x.get_property('language-code'))
			# Only enable the audio track menu item if there's more than one audio track.
			if (len(self.audioTracks) > 1):
				self.wTree.get_widget('mnuiAudioTrack').set_sensitive(True)
			else:
				self.wTree.get_widget('mnuiAudioTrack').set_sensitive(False)
			# Set the play/pause image to pause.
			self.setPlayPauseImage(1)
			# Create the timers.
			self.createPlayTimers()
			
		elif (playerTools.isPauseMsg(msg)):
			# It's just been paused or stopped.
			self.setPlayPauseImage(0)
			# Destroy the play timers.
			self.destroyPlayTimers()
			# Update the progress bar.
			self.progressUpdate()
			
		if (playerTools.isStopMsg(msg)):
			# Draw the background image.
			self.drawMovieWindowImage()
	
	
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
				
	
	def showOpenDialogue(self, widget=None):
		## Shows the open file dialogue.
		# Prepare the dialogue.
		dlg = dialogues.OpenFile(self.mainWindow, self.lastFolder)

		if (dlg.file):
			# If the response is OK, play the file.		
			self.playFile(dlg.file)
			# Also set the last folder.
			self.lastFolder = dlg.dir
	
	
	def openDroppedFile(self, widget, context, x, y, selection_data, info, time):
		## Opens a file after a drag and drop.
		# Split all the files that were input.
		uris = selection_data.data.strip().split()
		# Can only play one file at once, so use the first one.
		uri = uris[0]
		
		if (uri.startswith('file://')):
			# If it starts with file, remove it.
			file = urllib.url2pathname(uri[7:]).strip('\r\n\x00')
		
		# Actually play the file.
		self.playFile(file)
		# Finish the drag.
		context.finish(True, False, time)
	
	
	def playFile(self, file):
		## Plays the file 'file' (Could also be a URI).
		# First, stop the player.
		self.player.stop()
		# Set the audio and subtitles tracks to 0
		self.player.setAudioTrack(0)
		self.player.setSubtitleTrack(0)
		
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
			if (tot >= 0): self.progressBar.set_fraction(pld / tot)
		
		# Convert played & total time to integers
		p, t = int(pld), int(tot)
		# Add the data to the progress bar's text.
		text = ""
		text += useful.secToStr(p)
		if (tot >= 0):
			text += " / "
			text += useful.secToStr(t)
		self.progressBar.set_text(text)
		
	
	def seekStart(self, widget, event):
		## Sets that seeking has started.
		x, y, state = event.window.get_pointer()
		if (state & gtk.gdk.BUTTON1_MASK and not self.player.isStopped()):
			# It it's button 1, start seeking.
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
		frac = float(x) / maxX
		if (frac > 1): frac = 1
		if (frac < 0): frac = 0
		
		# Set the progress bar to the new data.
		self.progressUpdate((frac * dur), dur)
		
	
	def changeVolume(self, widget):
		## Change the volume to that indicated by the volume bar.
		vol = widget.get_value()
		self.player.setVolume(vol)
		# Set the new volume on the configuration.
		self.cfg.set("audio/volume", vol)
	
	
	def setPlayPauseImage(self, playing):
		## Changes the play/pause image according to the argument.
		# Set the size.
		size = gtk.ICON_SIZE_SMALL_TOOLBAR
		# Set the icon accordingly (Not playing -> Pause button, otherwise, play.)
		img = gtk.image_new_from_stock('gtk-media-play' if (not playing) else 'gtk-media-pause', size)
		
		# Actually set the icon.
		self.wTree.get_widget("btnPlayToggle").set_image(img)
	
	
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
	
	
	def drawMovieWindowImage(self):
		# Get the image file.
		image = '../images/whaawmp.png'
		# Create a pixbuf from the file.
		pixbuf = gtk.gdk.pixbuf_new_from_file(image)
		# Draw the image on the file.
		self.movieWindow.window.draw_pixbuf(self.movieWindow.get_style().black_gc, pixbuf, 0, 0, 0, 0)
		
	
	def showAboutDialogue(self, widget):
		dialogues.AboutDialogue(self.gladefile, self.mainWindow, self.__version__)
	
	
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
		if (dlg.URI != None):
			# If something was input, play it.
			self.playFile(dlg.URI)
	
	def showAudioTracksDialogue(self, widget):
		# Show the audio track selection dialogue (hopefully will handle subtitles too soon.
		dlg = dialogues.SelectAudioTrack(self.mainWindow, self.audioTracks, self.player)
	
	def stopPlayer(self, widget):
		# Just a transfer call as player.stop takes only 1 argument.
		self.player.stop()
	
	
	def __init__(self, main, __version__, options, args):
		# Set the last folder to the directory from which the program was called.
		self.lastFolder = main.origDir
		self.cfg = main.cfg
		self.__version__ = __version__
		self.options = options
		
		# Create & prepare the player for playing.
		self.preparePlayer()
		
		windowname = "main"
		self.wTree = gtk.glade.XML(self.gladefile, windowname)
		
		dic = { "on_main_delete_event" : self.quit,
		        "on_mnuiQuit_activate" : self.quit,
		        "on_mnuiOpen_activate" : self.showOpenDialogue,
		        "on_mnuiOpenURI_activate" : self.showOpenURIDialogue,
		        "on_btnPlayToggle_clicked" : self.togglePlayPause,
		        "on_btnStop_clicked" : self.stopPlayer,
		        "on_pbarProgress_button_press_event" : self.seekStart,
		        "on_pbarProgress_button_release_event" : self.seekEnd,
		        "on_pbarProgress_motion_notify_event" : self.progressBarMotion,
		        "on_vscVolume_value_changed" : self.changeVolume,
		        "on_mnuiFS_activate" : self.toggleFullScreen,
		        "on_btnLeaveFullscreen_clicked" : self.toggleFullScreen,
		        "on_videoWindow_expose_event" : self.videoWindowExpose,
		        "on_videoWindow_configure_event" : self.videoWindowConfigure,
		        "on_main_key_press_event" : self.windowKeyPressed,
		        "on_videoWindow_button_press_event" : self.videoWindowClicked,
		        "on_videoWindow_scroll_event" : self.videoWindowScroll,
		        "on_mnuiAbout_activate" : self.showAboutDialogue,
		        "on_main_drag_data_received" : self.openDroppedFile,
		        "on_videoWindow_motion_notify_event" : self.videoWindowMotion,
		        "on_videoWindow_leave_notify_event" : self.videoWindowLeave,
		        "on_videoWindow_enter_notify_event" : self.videoWindowEnter,
		        "on_mnuiPreferences_activate" : self.showPreferencesDialogue,
		        "on_mnuiPlayDVD_activate" : self.showPlayDVDDialogue,
		        "on_mnuiAudioTrack_activate" : self.showAudioTracksDialogue }
		self.wTree.signal_autoconnect(dic)
		
		# Get several items for access later.
		self.mainWindow = self.wTree.get_widget(windowname)
		self.progressBar = self.wTree.get_widget("pbarProgress")
		self.movieWindow = self.wTree.get_widget("videoWindow")
		self.nowPlyLbl = self.wTree.get_widget("lblNowPlaying")
		self.volAdj = self.wTree.get_widget("vscVolume").get_adjustment()
		# Set the window to allow drops
		self.mainWindow.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY)
		# Update the progress bar.
		self.progressUpdate()
		# Get the volume from the configuration.
		self.volAdj.value = self.cfg.getFloat("audio/volume")
		# Set up the default flags.
		self.fsActive = False
		self.controlsShown = True
		self.seeking = False
		# Play a file (if it was specified on the command line).
		if (len(args) > 0):
			filename = args[0]
			if ((not os.path.isdir(filename) and os.path.exists(filename)) or '://' in filename):
				self.playFile(filename)
			else:
				filename = main.origDir + os.sep + filename
				if (not os.path.isdir(filename) and os.path.exists(filename)):
					self.playFile(filename)
			
		self.progressUpdate()
		
		# Configure the video area.
		self.videoWindowConfigure(self.movieWindow)
		if (options.fullscreen):
			# If the fullscreen option was passed, start fullscreen.
			self.videoActivateFullScreen()
		
		# Enter the GTK main loop.
		gtk.main()
