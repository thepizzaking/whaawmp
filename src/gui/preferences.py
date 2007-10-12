# -*- coding: utf-8 -*-

#  Preferences Dialog
#  Copyright © 2007, Jeff Bailes <thepizzaking@gmail.com>
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

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject
from common import useful, lists, mutagenTagger
from common.config import cfg
from common.gstPlayer import player

class Dialogue:
	def __init__(self, main, parent):
		## Shows the preferences dialogue.
		# Sets some variables for easier access.
		self.main = main
		
		# Then create the dialogue and connect the signals.
		windowname = 'PreferencesDlg'
		self.wTree = gtk.glade.XML(useful.gladefile, windowname, useful.sName)
		
		dic = { "on_PreferencesDlg_delete_event" : self.closeWindow,
		        "on_checkbox_toggled" : self.checkboxToggle,
		        "on_scrollbar_changed" : self.adjustmentChanged,
		        "on_spinbutton_changed" : self.adjustmentChanged,
		        "on_entry_changed" : self.entryChanged,
		        "on_scrollbar_colour_changed": self.scrollbarColourScroll,
		        "on_btnVideoDefaults_clicked" : self.resetVideoDefaults,
		        "on_chkForceAspect_toggled" : self.toggleForceAspect,
		        "on_btnClose_clicked" : self.closeWindow }
		self.wTree.signal_autoconnect(dic)
		
		# Create a dictionary for checkboxes and their associated settings.
		self.chkDic = { self.wTree.get_widget('chkInstantSeek') : "gui/instantseek",
		                self.wTree.get_widget('chkDisableScreensaver') : "misc/disablescreensaver",
		                self.wTree.get_widget('chkShowTimeRemaining') : "gui/showtimeremaining",
		                self.wTree.get_widget('chkEnableVisualisation') : "gui/enablevisualisation",
		                self.wTree.get_widget('chkHideVideoWindow') : "gui/hidevideowindow",
		                self.wTree.get_widget('chkFileAsTitle') : "gui/fileastitle",
		                self.wTree.get_widget('chkForceAspect') : "video/force-aspect-ratio" }
		# And one for the scrollbars.
		self.adjDic = { self.wTree.get_widget('spnMouseTimeout') : "gui/mousehidetimeout",
		                self.wTree.get_widget('spnVolumeScrollChange') : "gui/volumescrollchange",
		                self.wTree.get_widget('hscBrightness') : "video/brightness",
		                self.wTree.get_widget('hscContrast') : "video/contrast",
		                self.wTree.get_widget('hscHue') : "video/hue",
		                self.wTree.get_widget('hscSaturation') : "video/saturation" }
		
		# And entries.
		self.entDic = {self.wTree.get_widget('entTagSyntax') : "gui/tagsyntax"}
		
		# More easy access.
		self.window = self.wTree.get_widget(windowname)
		# Set the parent window to the widget passed (hopefully the main window.)
		self.window.set_transient_for(parent)
		# Disable video options that aren't available.
		if (not player.colourSettings):
			for x in lists.colourSettings:
				self.wTree.get_widget('hsc' + x).set_sensitive(False)
			self.wTree.get_widget('btnVideoDefaults').set_sensitive(False)
		if (not player.aspectSettings):
			self.wTree.get_widget('chkForceAspect').set_sensitive(False)
		
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
			x.set_active(cfg.getBool(self.chkDic[x]))
		
		for x in self.adjDic:
			x.set_value(cfg.getFloat(self.adjDic[x]))
		
		for x in self.entDic:
			x.set_text(cfg.getStr(self.entDic[x]))
		
		self.wTree.get_widget('entTagSyntax').set_sensitive(mutagenTagger.avail)
	
	
	def checkboxToggle(self, widget):
		## A generic function called when toggling a checkbox.
		cfg.set(self.chkDic[widget], widget.get_active())
	
	def adjustmentChanged(self, widget):
		## A generic function called when scrolling a scrollbar.
		cfg.set(self.adjDic[widget], widget.get_value())
	
	def entryChanged(self, widget):
		## A generic function called when text in an entry is changed.
		cfg.set(self.entDic[widget], widget.get_text())
	
	
	def scrollbarColourScroll(self, widget):
		## Reads all the colour settings and sets them.
		if (player.playingVideo()):
			# Set it if a video is playing.
			player.setBrightness(cfg.getInt("video/brightness"))
			player.setContrast(cfg.getInt("video/contrast"))
			player.setHue(cfg.getInt("video/hue"))
			player.setSaturation(cfg.getInt("video/saturation"))
	
	
	def resetVideoDefaults(self, widget):
		## Resets all the settings to 0.
		for x in lists.colourSettings:
			self.wTree.get_widget('hsc' + x).set_value(0)
			
		# Call the colour changed settings so they are changed in the video.
		self.scrollbarColourScroll(widget)
	
	
	def toggleForceAspect(self, widget):
		## Sets force aspect ratio to if it's set or not.
		if (player.playingVideo()):
			player.setForceAspectRatio(cfg.getBool("video/force-aspect-ratio"))
			self.main.videoWindowConfigure(self.main.videoWindow)
