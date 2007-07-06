#!/usr/bin/env python

# Other Dialogues
# Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
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

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade

class AboutDialogue:
	def __init__(self, gladefile, version):
		## Shows the about dialogue.
		windowname = 'AboutDlg'
		tree = gtk.glade.XML(gladefile, windowname)
		
		dlg = tree.get_widget(windowname)
		# Sets the correct version.
		dlg.set_version(version)
		
		# Run the destroy the dialogue.
		dlg.run()
		dlg.destroy()


class OpenFile:
	def __init__(self, parent, loc):
		## Does an open dialogue, puts the directory into dir and the file
		## in to file.
		# Create the dialogue.
		self.dlg = gtk.FileChooserDialog(("Choose a file"), parent,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		# Set the current folder to the one passed.
		self.dlg.set_current_folder(loc)
		
		# Run the dialogue, then hide it.
		res = self.dlg.run()
		self.dlg.hide()
		
		# Save the current folder.
		self.dir = self.dlg.get_current_folder()
		self.file = self.dlg.get_filename() if (res == gtk.RESPONSE_OK) else None
		
		# Destroy the dialogue.
		self.dlg.destroy()


class PreferencesDialogue:
	def __init__(self, main, parent):
		## Shows the preferences dialogue.
		# Sets some variables for easier access.
		self.cfg = main.cfg
		self.player = main.player
		
		# Then create the dialogue and connect the signals.
		windowname = 'PreferencesDlg'
		self.wTree = gtk.glade.XML(main.gladefile, windowname)
		
		dic = { "on_PreferencesDlg_delete_event" : self.closeWindow,
		        "on_chkInstantSeek_toggled" : self.toggleInstantSeek,
		        "on_hscBrightness_value_changed" : self.adjustBrightness,
		        "on_hscContrast_value_changed" : self.adjustContrast,
		        "on_hscHue_value_changed" : self.adjustHue,
		        "on_hscSaturation_value_changed" : self.adjustSaturation,
		        "on_btnVideoDefaults_clicked" : self.resetVideoDefaults,
		        "on_chkForceAspect_toggled" : self.toggleForceAspect,
		        "on_btnClose_clicked" : self.closeWindow }
		self.wTree.signal_autoconnect(dic)
		
		# More easy access.
		self.window = self.wTree.get_widget(windowname)
		# Set the parent window to the widget passed (hopefully the main window.)
		self.window.set_transient_for(parent)
		
		# Load the preferences.
		self.loadPreferences()
		# Run the dialogue.
		self.window.run()
	
	
	def closeWindow(self, widget, event=None):
		## Destroys the preferences window.
		self.window.destroy()
	
	
	def loadPreferences(self):
		## Reads the preferences from the config and displays them.
		self.wTree.get_widget('chkInstantSeek').set_active(self.cfg.getBool("gui/instantseek"))
		
		for x in ['Brightness', 'Contrast', 'Hue', 'Saturation']:
			self.wTree.get_widget('hsc' + x).set_value(self.cfg.getInt("video/" + x))
		
		self.wTree.get_widget('chkForceAspect').set_active(self.cfg.getBool("video/force-aspect-ratio"))
	
	
	def toggleInstantSeek(self, widget):
		## Toggles the instant seek of the player.
		self.cfg.set("gui/instantseek", widget.get_active())
	
	
	def resetVideoDefaults(self, widget):
		## Resets all the settings to 0.
		for x in ['Brightness', 'Contrast', 'Hue', 'Saturation']:
			self.wTree.get_widget('hsc' + x).set_value(0)
	
	
	def adjustBrightness(self, widget):
		## Change the brightness of the video.
		val = widget.get_value()
		self.cfg.set("video/brightness", val)
		if (self.player.playingVideo()):
			# Set it if a video is playing.
			self.player.setBrightness(val)
	
	def adjustContrast(self, widget):
		## Same as Brightness, but for contrast.
		val = widget.get_value()
		self.cfg.set("video/contrast", val)
		if (self.player.playingVideo()):
			self.player.setContrast(val)
	
	def adjustHue(self, widget):
		## Same as Brightness, but for hue.
		val = widget.get_value()
		self.cfg.set("video/hue", val)
		if (self.player.playingVideo()):
			self.player.setContrast(val)
	
	def adjustSaturation(self, widget):
		## Same as Brightness, but for saturation.
		val = widget.get_value()
		self.cfg.set("video/saturation", val)
		if (self.player.playingVideo()):
			self.player.setContrast(val)
	
	def toggleForceAspect(self, widget):
		## Sets force aspect ratio to if it's checked or not.
		val = widget.get_active()
		self.cfg.set("video/force-aspect-ratio", val)
		if (self.player.playingVideo()):
			self.player.setForceAspectRatio(val)



class OpenURI:
	def __init__(self, parent):
		## Creates an openURI dialogue.
		# Create the dialogue.
		dlg = gtk.Dialog(("Input a URI"), parent,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		# Create the label and entry, then pack them.
		label = gtk.Label("Enter the URI:")
		label.set_alignment(0, 0.5)
		entry = gtk.Entry()
		entry.set_size_request(350, -1)
		dlg.vbox.pack_start(label)
		dlg.vbox.pack_start(entry)
		# Show all the dialogues.
		dlg.show_all()
		
		# Run the dialogue, then hide it.
		res = dlg.run()
		dlg.hide()
		
		# Save the URI if OK was pressed.
		self.URI = entry.get_text() if (res == gtk.RESPONSE_OK) else None
		# Destroy the dialogue.
		dlg.destroy()
		
