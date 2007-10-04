#  A few useful functions for Whaaw! Media Player.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
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

import os, gobject, sys

# Nice variables.
sName = 'whaawmp'
lName = _('Whaaw! Media Player')
version = '0.2.3'
origDir = os.getcwd()
dataDir = '@datadir@'
if (dataDir == '@' + 'datadir@'): dataDir = os.path.join(sys.path[0], '..')
gladefile = os.path.join(dataDir, 'glade', sName + '.glade')

## Set the basic timer function accordingly since using timeout_add_seconds
# is probably a better idea (Argument is in seconds).
# TODO: Remove this when glib 2.14 becomes more widespread.
if (gobject.glib_version < (2,14)):
	print "Old timer method used, since glib version is pre-2.14"
	addTimer = lambda t, f: gobject.timeout_add(sToms(t), f)
else:
	addTimer = lambda t, f: gobject.timeout_add_seconds(t, f)

# Executions with no output.
hiddenExec = lambda x: os.system(x +  '>/dev/null 2>/dev/null &')

linkHandler = 'xdg-open'

# Converts nanoseconds to seconds.
nsTos = lambda ns: float(ns) / 1000000000
# Seconds to miliseconds.
sToms = lambda s: 1000 * s


def secToStr(s):
	## Converts seconds into a string of H:M:S
	h = s / 3600
	m = (s % 3600) / 60
	s = s % 60
	# Only print hours if it doesn't equal 0.
	if (h != 0):
		return '%d:%02d:%02d' % (h, m, s)
	else:
		return '%d:%02d' % (m, s)

def toRange(val, min, max):
	## Returns a value within the requested range. ie, checks that val
	## lies within it, if it doesn't make is so.
	if (val < min): val = min
	if (val > max): val = max
	return val

checkLinkHandler = not(hiddenExec('which %s' % linkHandler))

def URLorMailOpen(link, type=None):
	## Opens a url or an e-mail composer (only uses exo-open so far)
	if (type == 'mail' and 'mailto:' not in link):
		# If the address doesn't have mailto:, add it.
		link = 'mailto:' + link
	# Open the link in the default program.
	os.system('%s "%s"' % (linkHandler, link))
