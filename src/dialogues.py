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
		windowname = 'about'
		tree = gtk.glade.XML(gladefile, windowname)
		
		dlg = tree.get_widget(windowname)
		# Sets the correct version.
		dlg.set_version(version)
		
		# Run the destroy the dialogue.
		dlg.run()
		dlg.destroy()


class openFile:
	def __init__(self, widget, loc):
		## Does an open dialogue, puts the directory into dir and the file
		## in to file.
		# Create the dialogue.
		self.dlg = gtk.FileChooserDialog(("Choose a file"), widget,
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
		
		
