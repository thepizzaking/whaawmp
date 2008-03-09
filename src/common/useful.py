# -*- coding: utf-8 -*-

#  A few useful functions for Whaaw! Media Player.
#  Copyright © 2007-2008, Jeff Bailes <thepizzaking@gmail.com>
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
version = '0.2.7'
origDir = os.getcwd()
dataDir = '@datadir@'
if (dataDir == '@' + 'datadir@'): dataDir = os.path.join(sys.path[0], '..')
gladefile = os.path.join(dataDir, 'glade', sName + '.glade')
# Other things stored here are:
#mainWin (the main window)
#lastDir (the last directory used in the open file dialogue etc)

# Executions with no output.
hiddenExec = lambda x: os.system(x +  '>/dev/null 2>/dev/null &')

linkHandler = 'xdg-open'

# Converts nanoseconds to seconds.
nsTos = lambda ns: float(ns) / 1000000000
# Seconds to miliseconds.
sToms = lambda s: 1000 * s

def strPartition(str, separator):
	## Replacement for str.partition (not available in py 2.4)
	try:
	    first, last = str.split(separator,1)
	    return first, separator, last
	except ValueError:
		return (str, "", "")

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
	## Opens a url or an e-mail composer (only uses xdg-open so far)
	if (type == 'mail' and 'mailto:' not in link):
		# If the address doesn't have mailto:, add it.
		link = 'mailto:' + link
	# Open the link in the default program.
	os.system('%s "%s"' % (linkHandler, link))

def tagsToTuple(str):
	## Takes a string and returns a list of eihter (True, *tag*) or (False, *str*)
	tags = []
	# First split the string at { (start of a tag).
	split = strPartition(str, '{')
	while (len(split[1])):
		# While we aren't done.
		# Append the bit before the tag.
		tags.append((False, split[0]))
		# Split at } (end of tag).
		split = strPartition(split[2], '}')
		# Append the tag to the list.
		tags.append((True, split[0]))
		# Split at the { again.
		split = strPartition(split[2], '{')
	return tags

# Pix data for hidden cursors.
hiddenCursorPix = """/* XPM */
    		         static char * invisible_xpm[] = {
    		         "1 1 1 1",
    		         "       c None",
    				 " "};"""

# Modify a window's height by a set amount.
def modifyWinHeight(window, change):
	(w, h) = window.get_size()
	window.resize(w, h + change)

# Convert tags to a readable string.
def tagsToStr(tags):
	# If tags is empty, don't try and read anything, just send a notification.
	if (not tags): return _("No tags available")
	tagStr = ""
	for x in tags.keys():
		# For all the items in the dictionary, add them to the string.
		tagStr += '\t' + x + ':\n'
		tagStr += '\t\t' + str(tags[x]) + '\n'
	return tagStr

# Converts a URI/File into just the files name (no preceeding directories)
def uriToFilename(file, ext=True):
	# Get rid of preceeding directories.
	name = file.split(os.sep)[-1]
	# Get rid of the extension (if requested).
	if ((not ext) and ('.' in name)):
		name = name[:-(len(name.split('.')[-1]) + 1)]
	
	return name
	

# Convert a version tuple to a sting.
verTupleToStr = lambda tuple: '.'.join(map(str, tuple))
