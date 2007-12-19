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
	def __init__(self):
		dbus.service.Object.__init__(self, name, "/IntObject")
	
	@dbus.service.method("org.gna.whaawmp", "")
	def playfile(self):
		print 'a'

if avail:
	DBusGMainLoop(set_as_default=True)
	
	bus = dbus.SessionBus()
	name = dbus.service.BusName("org.gna.whaawmp", bus)
	
	busObject = IntObject()

'''
The following code will make it print 'a':
ro = bus.get_object('org.gna.whaawmp', '/IntObject')
iface = dbus.Interface(ro, "org.gna.whaawmp")
iface.playfile()
'''
