# -*- coding: utf-8 -*-

#  Other Dialogues
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
import os
from common import lists, useful
from common.config import cfg
from common.gstPlayer import player

class AboutDialogue:
	def __init__(self, parent):
		## Shows the about dialogue.
		windowname = 'AboutDlg'
		tree = gtk.glade.XML(useful.gladefile, windowname, useful.sName)
		
		dlg = tree.get_widget(windowname)
		# Set the name.
		## TODO!!: Remove this when glib 2.14 is more widespread (or GTK 2.12
		# it's one of them), because it defaults to application name set.
		if (gobject.glib_version < (2,14)): dlg.set_name(useful.lName)
		# Sets the correct version.
		dlg.set_version(useful.version)
		# Set the parent to the main window.
		dlg.set_transient_for(parent)
		# Set the logo.
		dlg.set_logo(gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(useful.dataDir, 'images', 'whaawmp800.png'), 200, 200))
		
		# Run, then destroy the dialogue.
		dlg.run()
		dlg.destroy()


class OpenFile:
	def __init__(self, parent, loc):
		## Does an open dialogue, puts the directory into dir and the file
		## in to file.
		# Create the dialogue.
		dlg = gtk.FileChooserDialog(_("Choose a file to Open"), parent,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		# Set the current folder to the one passed.
		dlg.set_current_folder(loc)
		
		# Add the file filter.
		filter = gtk.FileFilter()
		filter.set_name(_("Supported Media"))
		for x in lists.compatFiles:
			filter.add_mime_type(x)
		dlg.add_filter(filter)
		# How about an all files one too.
		filter = gtk.FileFilter()
		filter.set_name(_("All Files"))
		filter.add_pattern('*')
		dlg.add_filter(filter)
		
		# Run the dialogue, then hide it.
		res = dlg.run()
		dlg.hide()
		
		# Save the current folder.
		self.dir = dlg.get_current_folder()
		self.file = dlg.get_filename() if (res == gtk.RESPONSE_OK) else None
		
		# Destroy the dialogue.
		dlg.destroy()


class PlayDVD:
	def __init__(self, parent):
		## Creates the play DVD dialogue.
		# Create the dialogue.
		dlg = gtk.Dialog(_("Play DVD"), parent,
		                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                               gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		# Create the Labels, checkboxes and spin buttons.
		label = gtk.Label(_("Select options:"))
		label.set_alignment(0, 0.5)
		chkTitle = gtk.CheckButton(_("Title: "))
		spnTitle = gtk.SpinButton(gtk.Adjustment(1, 1, 500, 1, 1, 1))
		# Add them to a dictionary so I can handle all the checkboxes with
		# a single function.
		self.spnDic = { chkTitle : spnTitle }
		# Start the packing.
		dlg.vbox.pack_start(label)
		
		for x in self.spnDic:
			self.spnDic[x].set_sensitive(False)
			x.connect("toggled", self.chkToggled)
			
			# Some of these options don't work all that well yet, so disable
			# them unless specifically told to show them.
			hbox = gtk.HBox()
			hbox.pack_start(x)
			hbox.pack_start(self.spnDic[x])
			dlg.vbox.pack_start(hbox)
		
		# Set the default response.
		dlg.set_default_response(gtk.RESPONSE_OK)
		# Show all the widgets, then run it.
		dlg.show_all()
		self.res = True if (dlg.run() == gtk.RESPONSE_OK) else False
		dlg.hide()
		
		# Save all the values.
		self.Title = int(spnTitle.get_value()) if (chkTitle.get_active()) else None
		
		# Finally, destroy the widget.
		dlg.destroy()
	
	
	def chkToggled(self, widget):
		# Enables and disables the spin buttons when the checkboxes are checked.
		self.spnDic[widget].set_sensitive(widget.get_active())
	


class OpenURI:
	def __init__(self, parent):
		## Creates an openURI dialogue.
		# Initially flag the response as None.
		self.res = None
		# Create the dialogue.
		dlg = gtk.Dialog(_("Open a URI"), parent,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		# Create the label and entry, then pack them.
		label = gtk.Label(_("Enter the URI:"))
		label.set_alignment(0, 0.5)
		entry = gtk.Entry()
		entry.set_size_request(350, -1)
		entry.connect('activate', self.onResponse, True, dlg)
		dlg.vbox.pack_start(label)
		dlg.vbox.pack_start(entry)
		# Show all the dialogues.
		dlg.show_all()
		
		# Run the dialogue, then hide it.
		self.onResponse(entry, (True if (dlg.run() == gtk.RESPONSE_OK) else False), dlg)
	
	def onResponse(self, entry, res, dlg):
		# If a result has already been obtained, cancel the call.
		if (self.res is not None):
			return
		else:
			self.res = res
		# Hide the dialogue.
		dlg.hide()
		
		# Save the URI if OK was pressed.
		self.URI = entry.get_text() if (self.res) else None
		# Destroy the dialogue.
		dlg.destroy()


class SelectAudioTrack:
	def __init__(self, parent, tracks):
		cur = player.getAudioTrack()
		# Creates an audio track selector dialogue.
		dlg = gtk.Dialog(_("Select Tracks"), parent,
		                  buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
		
		# Create the label.
		label = gtk.Label(_("Audio:"))
		label.set_alignment(0, 0.5)
		dlg.vbox.pack_start(label)
		# For all the tracks, create a radio button.
		group = gtk.RadioButton()
		buttons = []
		for x in range(len(tracks)):
			button = gtk.RadioButton(group, '%d. %s' % (x, tracks[x]))
			button.connect('toggled', self.buttonToggled, x)
			dlg.vbox.pack_start(button)
			buttons.append(button)
		
		# Set the current active button to active.
		buttons[cur].set_active(True)
		
		# Show all the dialogue and run it.
		dlg.show_all()
		dlg.run()
		dlg.destroy()
	
	def buttonToggled(self, widget, track):
		## When a button is toggled.
		if (player.getAudioTrack() != track):
			# If the current track differs to the selected one.
			# Get the current time, change the track, seek to 0 to activate
			# the new track, then seek back to the original position.
			# (Just changing the track didn't work)
			t = player.getPlayed()
			player.setAudioTrack(track)
			player.seek(0)
			player.seek(t)


class ErrorMsgBox:
	def __init__(self, parent, message, title=_('Error!')):
		## Creates an error message box (Use the MsgBox, just add an image).
		icon = gtk.image_new_from_stock('gtk-dialog-error', gtk.ICON_SIZE_DIALOG)
		# Run the message box, with the parameters already passed.
		MsgBox(parent, message, title, icon)


class MsgBox:
	def __init__(self, parent, message, title=_('Message'), icon=None):
		## Creates a message box containing the message 'message'.
		# Create the dialogue.
		dlg = gtk.Dialog(title, parent,
		                 buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		# Create the label containing the message & pack it in.
		hbox = gtk.HBox()
		if (icon):
			# If an icon was specified, pack it first.
			hbox.pack_start(icon)
		label = gtk.Label(message)
		hbox.pack_start(label)
		dlg.vbox.pack_start(hbox)
		# Show then destroy the dialogue.
		dlg.show_all()
		dlg.run()
		dlg.destroy()

