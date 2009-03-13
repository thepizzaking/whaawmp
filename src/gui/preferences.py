# -*- coding: utf-8 -*-

#  Preferences Dialog
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
#
#		The Whaaw! Media Player project hereby grants permission for non-GPL
#		compatible GStreamer plugins to be used and distributed together with
#       GStreamer and Whaaw! Media Player. This permission is above and beyond
#		the permissions granted by the GPL licence by which Whaaw! Media Player
#		is covered. (See COPYING file for more details)

import pygtk
pygtk.require('2.0')
import gtk, gobject
from common import useful, lists
from common.config import cfg
from common.gstPlayer import player
from common import dbusBus as msgBus

CFGS = 'cfg'
CLBKS = 'callback'

class Dialogue:
	def __init__(self, main, parent):
		## Shows the preferences dialogue.
		# Sets some variables for easier access.
		self.main = main
		
		# Create the dialogue and connect signals using gtk-builder.
		windowname = 'PreferencesDlg'
		self.wTree = gtk.Builder()
		self.wTree.add_from_file(useful.getBuilderFile('preferences'))
		
		
		dic = { "on_PreferencesDlg_delete_event" : self.closeWindow,
		        "on_checkbox_toggled" : self.checkboxToggle,
		        "on_scrollbar_changed" : self.adjustmentChanged,
		        "on_spinbutton_changed" : self.adjustmentChanged,
		        "on_cmbOnExtNewFile_changed" : self.extNewFileChanged,
		        "on_entry_changed" : self.entryChanged,
		        "on_btnVideoDefaults_clicked" : self.resetVideoDefaults,
		        "on_btnClose_clicked" : self.closeWindow }
		self.wTree.connect_signals(dic)
		
		# Create a dictionary for checkboxes and their associated settings.
		self.chkDic = { self.wTree.get_object('chkInstantSeek')         : {CFGS : "gui/instantseek"},
		                self.wTree.get_object('chkDisableScreensaver')  : {CFGS : "misc/disablescreensaver"},
		                self.wTree.get_object('chkShowTimeRemaining')   : {CFGS : "gui/showtimeremaining"},
		                self.wTree.get_object('chkEnableVisualisation') : {CFGS : "gui/enablevisualisation",
		                                                                  CLBKS : self.toggleEnableVis},
		                self.wTree.get_object('chkHideVideoWindow')     : {CFGS : "gui/hidevideowindow"},
		                self.wTree.get_object('chkFileAsTitle')         : {CFGS : "gui/fileastitle"},
		                self.wTree.get_object('chkForceAspect')         : {CFGS : "video/force-aspect-ratio",
		                                                                  CLBKS : self.toggleForceAspect} }
		# And one for the scrollbars.
		clrCbk = self.scrollbarColourScroll
		self.adjDic = { self.wTree.get_object('spnMouseTimeout')       : {CFGS : "gui/mousehidetimeout"},
		                self.wTree.get_object('hscBrightness')         : {CFGS : "video/brightness",
		                                                                 CLBKS : clrCbk},
		                self.wTree.get_object('hscContrast')           : {CFGS : "video/contrast",
		                                                                 CLBKS : clrCbk},
		                self.wTree.get_object('hscHue')                : {CFGS : "video/hue",
		                                                                 CLBKS : clrCbk},
		                self.wTree.get_object('hscSaturation')         : {CFGS : "video/saturation",
		                                                                 CLBKS : clrCbk} }
		
		# And entries.
		self.entDic = {self.wTree.get_object('entTagSyntax') : {CFGS : "gui/tagsyntax"}}
		
		# More easy access.
		self.window = self.wTree.get_object(windowname)
		# Set the parent window to the widget passed (hopefully the main window.)
		self.window.set_transient_for(parent)
		
		self.prepareAudioDevCmb()	
		# Load the preferences.
		self.loadPreferences()
		# Run the dialogue.
		self.window.run()
	
	
	def closeWindow(self, widget, event=None):
		## Destroys the preferences window.
		self.window.destroy()
	
	
	def loadPreferences(self):
		## Reads the preferences from the config and displays them.
		for x in self.chkDic:
			# Set all the checkboxes to their appropriate settings.
			x.set_active(cfg.getBool(self.chkDic[x][CFGS]))
		
		for x in self.adjDic:
			x.set_value(cfg.getFloat(self.adjDic[x][CFGS]))
		
		for x in self.entDic:
			x.set_text(cfg.getStr(self.entDic[x][CFGS]))
		
		self.wTree.get_object('cmbOnExtNewFile').set_active(cfg.getInt('misc/onextnewfile'))
	
	
	def checkboxToggle(self, widget):
		## A generic function called when toggling a checkbox.
		dicEntry = self.chkDic[widget]
		# First we change the config option apporpriately.
		cfg.set(dicEntry[CFGS], widget.get_active())
		# Then if there's a callback present, call it.
		if (CLBKS in dicEntry):
			dicEntry[CLBKS](widget)
	
	def adjustmentChanged(self, widget):
		## A generic function called when scrolling a scrollbar.
		# See above for description.
		dicEntry = self.adjDic[widget]
		cfg.set(dicEntry[CFGS], widget.get_value())
		if (CLBKS in dicEntry):
			dicEntry[CLBKS](widget)
	
	def entryChanged(self, widget):
		## A generic function called when text in an entry is changed.
		# See above for description.
		dicEntry = self.entDic[widget]
		cfg.set(dicEntry[CFGS], widget.get_text())
		if (CLBKS in dicEntry):
			dicEntry[CLBKS](widget)
	
	
	def scrollbarColourScroll(self, widget):
		## Reads all the colour settings and sets them.
		if (player.playingVideo()):
			# Set it if a video is playing.
			player.setBrightness(cfg.getFloat("video/brightness"))
			player.setContrast(cfg.getFloat("video/contrast"))
			player.setHue(cfg.getFloat("video/hue"))
			player.setSaturation(cfg.getFloat("video/saturation"))
	
	
	def resetVideoDefaults(self, widget):
		## Resets all the settings to their defaults (according to the list).
		for x in lists.colourSettings:
			self.wTree.get_object('hsc' + x).set_value(lists.defaultOptions['video/' + x.lower()])
			
		# Call the colour changed settings so they are changed in the video.
		self.scrollbarColourScroll(widget)
	
	
	def toggleForceAspect(self, widget):
		## Sets force aspect ratio to if it's set or not.
		if (player.playingVideo()):
			player.setForceAspectRatio(cfg.getBool("video/force-aspect-ratio"))
			self.main.videoWindowConfigure(self.main.videoWindow)
	
	def toggleEnableVis(self, widget):
		## Toggle enable visualisations.
		player.setVisualisation(widget.get_active())
	
	def extNewFileChanged(self, widget):
		## Changes the saved option for the external file action.
		cfg.set('misc/onextnewfile', widget.get_active())
	
	def prepareAudioDevCmb(self):
		## Prepares the audio device combo box.
		# Create the combo box for the selection.
		audioCmbBox = gtk.combo_box_new_text()
		self.wTree.get_object('hboxAudioDevice').pack_end(audioCmbBox)
		audioCmbBox.connect('changed', self.changeAudioDevice)
		audioCmbBox.show()
		# Get the available alsa devices.
		self.audioDevDic = msgBus.getAlsaDevices()
		# Append the non-alsa devices.
		for x in (_('Default/Auto'), _('Other (Set from config.ini)')):
			audioCmbBox.append_text(x)
		# For all the alsa devices, add them to the combo box.
		for x in self.audioDevDic:
			audioCmbBox.append_text('Alsa: %s (%s)' % (self.audioDevDic[x], x))
		# Set the preference according to the current device.
		cfgSink = cfg.getStr('audio/audiosink')
		cfgDevice = cfg.getStr('audio/audiodevice')
		if (cfgSink == 'alsasink' and cfgDevice in self.audioDevDic):
			# If we're set to use the alsa sink and the device has been detected.
			# Set that device as the one set (+1 is to account for the 'Other'
			# option at the top of the list.
			audioCmbBox.set_active(self.audioDevDic.keys().index(cfgDevice) + 2)
		elif (cfgSink in ('default', '')):
			# The 'default' option is set, corresponds to sink=default.
			audioCmbBox.set_active(0)
		else:
			# Otherwise set the 'Other' option.
			audioCmbBox.set_active(1)
	
	def changeAudioDevice(self, widget):
		## Changes the output audio device.
		# Get the active index.
		index = widget.get_active()
		if (index == 0):
			# This is the default/auto option.
			cfg.set('audio/audiosink', '')
			cfg.set('audio/audiodevice', '')
		elif (index >= 2):
			# We don't want to change the settings if the index is 1 (manually set)
			# or 0 (default/auto).
			# Set the sink, and the device (-1 to account for the 'other' option)
			cfg.set('audio/audiosink', 'alsasink')
			cfg.set('audio/audiodevice', self.audioDevDic.keys()[index - 2])
		
		# Set the audio sink.
		if (index != 1): player.setAudioSink()
