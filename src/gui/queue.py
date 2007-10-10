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
import os, urllib

from common import mutagenTagger as tagger

class queues():
	# The menu item widget, which is changed when the window closes.
	mnuiWidget = None
	
	# Sets the menu item to active/inactive.
	mnuiSet = lambda self, shown: self.mnuiWidget.set_active(shown)
	# Gets the length of the items in the list.
	length = lambda self: len(self.list)
	
	def close(self, widget, event):
		## Called to 'close' the window.
		# Just hide it.
		self.hide()
		# Return True so it doesn't get destroyed.
		return True
	
	def toggle(self, toShow=None):
		## Toggles the window shown or not.
		# If the destination state wasn't passed, do the inverse of its current state.
		if (toShow is None): toShow = not open
		if (toShow):
			# If we want it shown, show it.
			self.show()
		else:
			# Otherwise, hide it.
			self.hide()
	
	def show(self, force=False):
		## Shows the window.
		# Set the menu item to activated.
		self.mnuiSet(True)
		# Flag the window as open.
		open = True
		# Actually show it.
		self.window.show()
	
	def hide(self, force=False):
		## Hides the window.
		# Set the menu item to deactivated.
		self.mnuiSet(False)
		# Flag the window as closed.
		open = False
		# Hide the window.
		self.window.hide()
	
	def append(self, item):
		## Appends an item to the queue.
		# Create a new row.
		row = self.list.append()
		# Add the path and the interpreted name to the row item.
		self.list.set_value(row, 0, item)
		self.list.set_value(row, 1, tagger.getDispTitle(item))
	
	def clear(self, widget=None):
		## Clears the queue.
		self.list.clear()
	
	def getNextTrackRemove(self):
		## Gets the next track and removes it from the list.
		try:
			# Try and get the first list items path.
			path = self.list[0][0]
			# Remove it from the queue.
			self.remove(0)
			# Return the path.
			return path
		except IndexError:
			# Index error (queue empty), return None.
			return None
	
	# Removes a selected index from the queue.
	remove = lambda self, index: self.list.remove(self.list.get_iter(index))
	
	def removeSelected(self, widget):
		## Removes the selected item from the queue.
		# Get the item.
		tree, item = self.tree.get_selection().get_selected()
		# If we get the item, remove it.
		if (item): tree.remove(item)
	
	def enqueueDropped(self, widget, context, x, y, selection_data, info, time):
		## Adds dropped files to the end of the queue.
		# Split the files.
		uris = selection_data.data.strip().split()
		# Add all the items to the queue.
		for x in uris:
			uri = urllib.url2pathname(x)
			self.append(uri)
		# Finish the drag.
		context.finish(True, False, time)
	
	def __init__(self):
		## I'll commend this mess soon (maybe pull it out to its own function too.
		open = False
		self.list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.window = gtk.Window()
		self.window.set_title(_("Queue"))
		self.window.resize(250,250)
		self.window.connect('delete-event', self.close)
		self.window.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY)
		self.window.connect('drag-data-received', self.enqueueDropped)
		tooltips = gtk.Tooltips()
		self.tree = gtk.TreeView(self.list)
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn(_("Track"), renderer, text=1)
		self.tree.append_column(column)
		self.tree.set_reorderable(True)
		scrolly = gtk.ScrolledWindow()
		scrolly.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolly.add(self.tree)
		btnClear = gtk.Button()
		btnClear.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, 2))
		tooltips.set_tip(btnClear, _('Clear Queue'))
		btnClear.connect('clicked', self.clear)
		btnRemove = gtk.Button()
		btnRemove.set_image(gtk.image_new_from_stock(gtk.STOCK_REMOVE, 2))
		tooltips.set_tip(btnRemove, _('Remove item from Queue'))
		btnRemove.connect('clicked', self.removeSelected)
		hBox = gtk.HBox()
		hBox.pack_end(btnClear, False, False)
		hBox.pack_end(btnRemove, False, False)
		vBox = gtk.VBox()
		vBox.pack_start(scrolly)
		vBox.pack_start(hBox, False, False)
		self.window.add(vBox)
		vBox.show_all()

queue = queues()
