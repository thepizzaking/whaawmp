# -*- coding: utf-8 -*-

#  Other Dialogues
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

import pygtk
pygtk.require('2.0')
import gtk, gobject
import os
from common import lists, useful
from common.config import cfg
from common.gstPlayer import player
from common.signals import signals

class AboutDialogue:
	def __init__(self, parent):
		## Shows the about dialogue.
		# Make the Dialogue.
		dlg = gtk.AboutDialog()
		
		# Sets the correct version, etc, etc.
		# (Name already set in main.py (gobject.set_application_name)
		dlg.set_version(useful.version)
		dlg.set_title("About Whaaw! Media Player")
		dlg.set_copyright("Copyright 2011, Jeff Bailes")
		dlg.set_website("http://home.gna.org/whaawmp/")
		dlg.set_license(useful.licenceText)
		dlg.set_authors(["Jeff Bailes <thepizzaking@gmail.com>, 2007-2011."])
		dlg.set_translator_credits(_("translator-credits"))
		# Set the parent to the main window.
		dlg.set_transient_for(parent)
		# Set the logo.
		dlg.set_logo(gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(useful.dataDir, 'images', 'whaawmp800.png'), 200, 200))
		# Set the comment.
		dlg.set_comments("GTK+ %s, GStreamer %s" % (useful.verTupleToStr(gtk.gtk_version), useful.verTupleToStr(player.version)))
		
		# Run, then destroy the dialogue.
		dlg.run()
		dlg.destroy()


class OpenFile:
	def __init__(self, parent, loc, multiple=True, allowSub=False, useFilter=True, title=_("Choose a file to Open")):
		## Does an open dialogue, puts the directory into dir and the file
		## in to file.
		# Create the dialogue.
		dlg = gtk.FileChooserDialog(title, parent,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		# Add a subtitle checkbox (if allowed).
		if allowSub:
			chkSubs = gtk.CheckButton(_("Also Choose Subtitle Stream"))
			chkSubs.set_has_tooltip(True)
			chkSubs.set_tooltip_text(_("After choosing the file to open, also choose a subtitle stream."))
			self.chkSubs = chkSubs
			dlg.set_extra_widget(chkSubs)
		
		# Set the current folder to the one passed.
		dlg.set_current_folder(loc)
		# Let the dialogue support multiple files (if requested).
		dlg.set_select_multiple(multiple)
		
		# Add the file filter (if requested).
		if useFilter:
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
		self.files = dlg.get_filenames() if (res == gtk.RESPONSE_OK) else None
		
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
		spnTitle = gtk.SpinButton(gtk.Adjustment(1, 1, 500, 1, 1, 0))
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
		# Enter on the text input is also OK.
		spnTitle.connect('activate', self.onResponse, dlg, gtk.RESPONSE_OK)
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
	
	def onResponse(self, entry, dlg, response):
		# A call to pass the dialogues response.
		dlg.response(response)
	


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
	def __init__(self, message, title=_('Error!'), parent=None):
		## Creates an error message box (Use the MsgBox, just add an image).
		icon = gtk.image_new_from_stock('gtk-dialog-error', gtk.ICON_SIZE_DIALOG)
		# Run the message box, with the parameters already passed.
		MsgBox(message, title, icon, parent=parent)


class MsgBox:
	def __init__(self, message, title=_('Message'), icon=None, parent=None):
		## Creates a message box containing the message 'message'.
		if (not parent): parent = useful.mainWin
		# Create the dialogue.
		dlg = gtk.Dialog(title, parent,
		                 buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		# Create the label containing the message & pack it in.
		hbox = gtk.HBox()
		if (icon):
			# If an icon was specified, pack it first.
			hbox.pack_start(icon)
		label = gtk.Label(message)
		label.set_selectable(True)
		hbox.pack_start(label)
		dlg.vbox.pack_start(hbox)
		# Show then destroy the dialogue.
		dlg.show_all()
		dlg.run()
		dlg.destroy()

class SupportedFeatures:
	def __init__(self, parent):
		# Shows a list of supported features.
		dlg = gtk.Dialog(_("Supported Features"), parent,
		                 buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
		dlg.set_resizable(False)
		
		# Import the librarys needed to check availability.
		import common.dbusBus as bus
		
		# Create a dictionary with the library title and its availability.
		dic = {_("Dbus Message Bus"): bus.avail}
		
		for x in dic:
			# For all the items in the dictionary.
			# Make the availability easier to use.
			a = dic[x]
			# Make an image and assign to it an icon according to the feature's availability.
			img = gtk.Image()
			icon = gtk.STOCK_APPLY if a else gtk.STOCK_CANCEL
			img.set_from_stock(icon, 2)
			# Pack in the button and a label into an HBox,
			# pack the HBox into a VBox and then the VBox
			# into the dialogue.
			hbox = gtk.HBox(spacing=7)
			hbox.pack_start(img, False, False)
			hbox.pack_start(gtk.Label("%s - %s" % (x, _("Available") if a else _("Unavailable"))))
			vbox = gtk.VBox(spacing=7)
			vbox.set_border_width(10)
			vbox.pack_start(hbox, False, False)
			dlg.vbox.pack_start(vbox, False, False)
		
		# Displaying library versions.
		lbl = gtk.Label("<b>"+_("Library Versions:")+"</b>")
		lbl.set_use_markup(True)
		lbl.set_alignment(0, 0.5)
		vbox.pack_start(lbl)
		vbox.pack_start(gtk.Label("GTK+ - %s" % useful.verTupleToStr(gtk.gtk_version)))
		vbox.pack_start(gtk.Label("GStreamer - %s" % useful.verTupleToStr(player.version)))
		
		# Show run and destroy it.
		dlg.show_all()
		dlg.run()
		dlg.destroy()


def __init__():
	# Connect the error signal.
	signals.connect('error', ErrorMsgBox)

__init__()
