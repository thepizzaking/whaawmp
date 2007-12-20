# -*- coding: utf-8 -*-

#  Configuration Backend
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

from common.gstPlayer import player
from gui.queue import queue

try:
	import dbus
	import dbus.service
	from dbus.mainloop.glib import DBusGMainLoop
	avail = True
except ImportError:
	print _("Dbus import failed, dbus features will be unavailable")
	# Dummy D-Bus library (From exaile)
	class _Connection:
		get_object = lambda *a: object()
	class _Interface:
		__init__ = lambda *a: None
		ListNames = lambda *a: []
	class Dummy: pass
	dbus = Dummy()
	dbus.Interface = _Interface
	dbus.service = Dummy()
	dbus.service.method = lambda *a: lambda f: f
	dbus.service.Object = object
	dbus.SessionBus = _Connection
	avail = False


class IntObject(dbus.service.Object):
	def __init__(self, mainWindow):
		name = dbus.service.BusName("org.gna.whaawmp", bus)
		dbus.service.Object.__init__(self, name, "/IntObject")
		self.main = mainWindow
	
	@dbus.service.method("org.gna.whaawmp", "s")
	def playFile(self, file):
		queue.append(file)
		if (not player.getURI()): self.main.playNext()

if avail:
	DBusGMainLoop(set_as_default=True)
	
	bus = dbus.SessionBus()

class initBus:
	quitAfter = False
	
	def __init__(self, mainWin, options, args):
		try:
			self.prepareIface()
		except dbus.exceptions.DBusException:
			IntObject(mainWin)
			return
		
		# If it gets to here, whaawmp is already running.
		print _("Whaaw! Media Player is already running")
		
		# Flag that we should quit after this.
		self.quitAfter = True
		for x in args:
			self.iface.playFile(x)

			
	def prepareIface(self):
		ro = bus.get_object("org.gna.whaawmp", "/IntObject")
		self.iface = dbus.Interface(ro, "org.gna.whaawmp")
	

'''
Code to do something:
import dbus
bus = dbus.SessionBus()
ro = bus.get_object('org.gna.whaawmp', '/IntObject')
iface = dbus.Interface(ro, "org.gna.whaawmp")
iface.playFile("/home/jeff/Music/10cc/10cc - The Things We Do For Love.oga")
'''
