# -*- coding: utf-8 -*-

#  The queue dialogue.
#  Copyright © 2007-2009, Jeff Bailes <thepizzaking@gmail.com>
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
import os, urllib, urlparse
from gui import dialogues
from common import gstTagger as tagger
from common import useful
from common.signals import signals


class queues():
	# The menu item widget, which is changed when the window closes.
	mnuiWidget = None
	
	# Sets the menu item to active/inactive.
	mnuiSet = lambda self, shown: self.mnuiWidget.set_active(shown)
	# Gets the length of the items in the list.
	length = lambda self: len(self.list)
	# The play command to play a file.
	playCommand = None
	
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
		return toShow
	
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
		# Make sure 'item' is a URI.
		if ('://' not in item): item = 'file://' + item
		# Create a new row.
		row = self.list.append()
		# Add the path and the interpreted name to the row item.
		self.list.set_value(row, 0, item)
		# Initiate the tag reading process, but show the filename in case it fails.
		self.list.set_value(row, 1, useful.uriToFilename(item))
		tagger.fileTag.file(item, self.setItmTags)
		# The queue has changed.
		self.queueChanged()
	
	def setItmTags(self, uri, tags):
		## Sets the items tags and displays them (maybe not very efficient).
		dispTitle = tagger.getDispTitle(tags)
		# If not display title was returned, just pass..
		if not dispTitle: return
		# For all the items in the list, if they have that URI, add the tags.
		for x in range(len(self.list)):
			if (self.list[x][0] == uri):
				self.list[x][1] = dispTitle
	
	def appendMany(self, items):
		## Appends many queue items.
		for x in items:
			# For all the files, add them to the queue.
			queue.append(x if ('://' in x) else os.path.abspath(x))
	
	def clear(self, widget=None):
		## Clears the queue.
		self.list.clear()
		# The queue has changed.
		self.queueChanged()
	
	def getTrackRemove(self, no):
		## Gets the track with the index 'no' & removes it.
		try:
			# Try and get the list items path.
			path = self.list[no][0]
			# Remove it from the queue.
			self.remove(no)
			# Return the path.
			return path
		except:
			# Index error, just return None.
			return None
	
	# Get & remove the next track (top of queue)
	getNextTrackRemove = lambda self: self.getTrackRemove(0)

	
	def rowActivated(self, tree, path, view_column):
		## Plays the track that has been activated in the queue.
		## (Double click an item)
		self.playCommand(self.getTrackRemove(path[0]))
	
	def remove(self, index):
		# Removes a selected index from the queue.
		self.list.remove(self.list.get_iter(index))
		# The queue has changed.
		self.queueChanged()
	
	def removeSelected(self, widget):
		## Removes the selected item from the queue.
		# Get the item.
		tree, item = self.tree.get_selection().get_selected()
		# If we get the item, remove it.
		if (item):
			# Get the items index (for later).
			itmNo = self.tree.get_model().get_path(item)[0]
			tree.remove(item)
			# The queue has changed.
			self.queueChanged()
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
	
	def queueChanged(self):
		# The queue has changed.
		signals.emit('queue-changed', self.length())
	
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
	
	def startAddDialogue(self, widget):
		## Adds items to the queue from a file selection.
		dlg = dialogues.OpenFile(useful.mainWin, useful.lastFolder)
		
		if (dlg.files):
			# Append all the files to the queue.
			self.appendMany(dlg.files)
			# Set the last folder (if it exists).
			if (dlg.dir): useful.lastFolder = dlg.dir
	
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
		# Connect a callback for a row activated.
		self.tree.connect('row-activated', self.rowActivated)
		# Allow the queue to be drag & drop reorderable.
		self.tree.set_reorderable(True)
		# Add a scrolling widget, set automatic bar display, and add the tree to it.
		scrolly = gtk.ScrolledWindow()
		scrolly.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolly.add(self.tree)
		# Create a clear button which clears the queue.
		btnClear = gtk.Button()
		btnClear.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_SMALL_TOOLBAR))
		btnClear.connect('clicked', self.clear)
		# Add a remove button which removes the currently selected item.
		btnRemove = gtk.Button()
		btnRemove.set_image(gtk.image_new_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_SMALL_TOOLBAR))
		btnRemove.connect('clicked', self.removeSelected)
		# How about an 'add' button too.
		btnAdd = gtk.Button()
		btnAdd.set_image(gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_SMALL_TOOLBAR))
		btnAdd.connect('clicked', self.startAddDialogue)
		# Create a horizontal box and add the clear & remove buttons to it.
		hBox = gtk.HBox()
		hBox.pack_end(btnClear, False, False)
		hBox.pack_end(btnRemove, False, False)
		hBox.pack_end(btnAdd, False, False)
		# Create a vertical box and add the tree (in the scroll widget) and
		# the horizontal box with the buttons to it.
		self.qwin.pack_start(scrolly)
		self.qwin.pack_start(hBox, False, False)
		# Add tooltips to the buttons.
		btnClear.set_tooltip_text(_('Clear Queue'))
		btnRemove.set_tooltip_text(_('Remove item from Queue'))
		btnAdd.set_tooltip_text(_('Add items to queue'))
	
	def __init__(self):
		# Flag the window as closed.
		self.open = False
		# Create the window.
		self.createWindow()

queue = queues()
