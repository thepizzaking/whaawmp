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
	def toggle(self, toShow=None):
		if (toShow is None): toShow = not open
		if (toShow):
			self.show()
		else:
			self.hide()
	
	def show(self, force=False):
		self.window.show()
	
	def hide(self, force=False):
		self.window.hide()
	
	def __init__(self):
		open = False
		list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.window = gtk.Window()
		self.window.resize(250,250)
		tree = gtk.TreeView(list)
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Str", renderer, text=1)
		tree.append_column(column)
		tree.set_reorderable(True)
		scrolly = gtk.ScrolledWindow()
		scrolly.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolly.add(tree)
		scrolly.show()
		self.window.add(scrolly)
		tree.show()
		itm = list.append()
		list.set_value(itm, 1, "Hi, this queue isn't actually working yet!!")

queue = queues()
