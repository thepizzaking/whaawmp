# -*- coding: utf-8 -*-

#  The queue dialogue.
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
import gtk, gobject
import os, urllib, urlparse

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
		if (toShow is None): toShow = not self.open
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
		self.open = True
		# Actually show it.
		self.qwin.show_all()
	
	def hide(self, force=False):
		## Hides the window.
		# Set the menu item to deactivated.
		self.mnuiSet(False)
		# Flag the window as closed.
		self.open = False
		# Hide the window.
		self.qwin.hide()
	
	def append(self, item):
		## Appends an item to the queue.
		# Create a new row.
		row = self.list.append()
		# Add the path and the interpreted name to the row item.
		self.list.set_value(row, 0, item)
		self.list.set_value(row, 1, tagger.getDispTitle(item))
	
	def appendMany(self, items):
		## Appends many queue items.
		for x in items:
			# For all the files, add them to the queue.
			queue.append(x if ('://' in x) else os.path.abspath(x))
	
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
		if (item):
			# Get the items index (for later).
			itmNo = self.tree.get_model().get_path(item)[0]
			tree.remove(item)
			# Now to select a new item in the queue.
			# Get the new length of the queue.
			newLen = self.length()
			if (newLen > itmNo):
				# If the queue length is bigger than the item number, select
				# the item which is taking the old ones spot.
				self.tree.get_selection().select_path(itmNo)
			elif (newLen == itmNo and newLen > 0):
				# If the queue length is the same as the item number, there is
				# no item taking its place, chose the previous item (should be
				# the last one)
				self.tree.get_selection().select_path(itmNo - 1)
			else:
				# Don't do anything if the queue is now empty.
				pass
	
	def enqueueDropped(self, widget, context, x, y, selection_data, info, time):
		## Adds dropped files to the end of the queue.
		# Split the files.
		uris = selection_data.data.strip().split()
		# Add all the items to the queue.
		for uri in uris:
			path = urllib.url2pathname(urlparse.urlparse(uri)[2])
			self.append(path)
		# Finish the drag.
		context.finish(True, False, time)
	
	def createWindow(self):
		## Creates the window of the queue.
		# First create the list, it contains two strings (1st path, 2nd display).
		self.list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		# Create the queue window/box
		self.qwin = gtk.VBox()
		# Set size.
		self.qwin.set_size_request(-1,200)
		# Set the window up for draq & drop.
		self.qwin.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY)
		self.qwin.connect('drag-data-received', self.enqueueDropped)
		# Create the tree view.
		self.tree = gtk.TreeView(self.list)
		# Add a text renderer for the display column & add it to the view.
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn(_("Queued Tracks:"), renderer, text=1)
		self.tree.append_column(column)
		# Allow the queue to be drag & drop reorderable.
		self.tree.set_reorderable(True)
		# Add a scrolling widget, set automatic bar display, and add the tree to it.
		scrolly = gtk.ScrolledWindow()
		scrolly.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolly.add(self.tree)
		# Create a clear button which clears the queue.
		btnClear = gtk.Button()
		btnClear.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, 2))
		btnClear.connect('clicked', self.clear)
		# Add a remove button which removes the currently selected item.
		btnRemove = gtk.Button()
		btnRemove.set_image(gtk.image_new_from_stock(gtk.STOCK_REMOVE, 2))
		btnRemove.connect('clicked', self.removeSelected)
		# Create a horizontal box and add the clear & remove buttons to it.
		hBox = gtk.HBox()
		hBox.pack_end(btnClear, False, False)
		hBox.pack_end(btnRemove, False, False)
		# Create a vertical box and add the tree (in the scroll widget) and
		# the horizontal box with the buttons to it.
		self.qwin.pack_start(scrolly)
		self.qwin.pack_start(hBox, False, False)
		# Create a tooltip instance and add tooltips to the buttons.
		tooltips = gtk.Tooltips()
		tooltips.set_tip(btnClear, _('Clear Queue'))
		tooltips.set_tip(btnRemove, _('Remove item from Queue'))
	
	def __init__(self):
		# Flag the window as closed.
		self.open = False
		# Create the window.
		self.createWindow()

queue = queues()
