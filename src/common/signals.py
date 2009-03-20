# -*- coding: utf-8 -*-

#  A signal handler for Whaaw! Media Player.
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

class Signals:
	## A signals class for processing signals.
	def connect(self, message, func, *args):
		## Connects a message.
		info = {'function' : func,
		        'connArgs' : args}
		# If an entry doesn't exist, we need to create it.
		if (message not in self.signals): self.signals[message] = []
		# And append the function to the selected message.
		self.signals[message].append(info)
	
	def emit(self, message, *args):
		## Not really emit, just act on a call.
		try:
			# Try and get the informaton.
			infoList = self.signals[message]
		except KeyError:
			# If we get a key error, this message hasn't been connected.
			print _("Something went wrong, can't act on signal which hasn't been connected.")
			return
		
		for info in infoList:
			# For all the actions that have been connected, act on them.
			info['function'](*(info['connArgs'] + args))
	
	def __init__(self):
		self.signals = {}

signals = Signals()
