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

class queues():
	mnuiWidget = None
	
	mnuiSet = lambda self, shown: self.mnuiWidget.set_active(shown)
	
	def close(self, widget, event):
		self.hide()
		return True
	
	def toggle(self, toShow=None):
		if (toShow is None): toShow = not open
		if (toShow):
			self.show()
		else:
			self.hide()
	
	def show(self, force=False):
		self.mnuiSet(True)
		open = True
		self.window.show()
	
	def hide(self, force=False):
		self.mnuiSet(False)
		open = False
		self.window.hide()
	
	def append(self, item):
		row = self.list.append()
		self.list.set_value(row, 0, item)
	
	def getNextLocRemove(self):
		uri = self.list[0][0]
		self.list.remove(self.list.get_iter(0))
		return uri
	
	def __init__(self):
		open = False
		self.list = gtk.ListStore(gobject.TYPE_STRING)
		self.window = gtk.Window()
		self.window.resize(250,250)
		self.window.connect('delete-event', self.close)
		tree = gtk.TreeView(self.list)
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Queue not implemented yet.", renderer, text=0)
		tree.append_column(column)
		tree.set_reorderable(True)
		scrolly = gtk.ScrolledWindow()
		scrolly.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolly.add(tree)
		scrolly.show()
		self.window.add(scrolly)
		tree.show()

queue = queues()
