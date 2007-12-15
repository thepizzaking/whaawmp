# -*- coding: utf-8 -*-

#  A player module for gstreamer.
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

import os
try:
	# Try and import mutagen.
	import mutagen
	avail = True
except:
	# If it fails, print an error message.
	print _("Mutagen not available, all tagging fetures will be unavailable")
	avail = False

import useful
from common.config import cfg


def getTags(file):
	# Try and return the dictionary of tags.
	try:
		# If not .ogv, just do the mutagen.File
		return mutagen.File(file, tagType(file))
	except:
		return {}

def getTag(tags, tag):
	try:
		return tags[tag]
	except:
		return []

def getSTag(tags, tag):
	## Gets a single tag.
	# Get the list of tags.
	tagsi = getTag(tags, tag)
	# If it's empty, return None.
	if (tagsi == []): return None
	# Otherwise, return the first item.
	return tagsi[0]

def getDispTitle(file):
	## Gets the (window) title to be displayed from Tags / filename.
	# If no file was passed, return an empty string. 
	if (not file): return ""
	# Remove any file:// first.
	if (file.startswith('file:///')): file = file[7:]
	# Initialise the winTitle to empty.
	winTitle = ""
	# If the tagger is available.
	if avail:
		# Get all the tags.
		tags = getTags(file)
		# Flag that no tags have been added.
		noneAdded = True
		for x in useful.tagsToTuple(cfg.getStr('gui/tagsyntax')):
			# For all the items in the list produced by tagsToTuple.
			# New string = the associated tag if it's a tag, otherwise just the string.
			nStr = getSTag(tags, x[1]) if (x[0]) else x[1]
			if (nStr):
				# If there was a string.
				# Flag that a tag has been added if it's a tag.
				if (x[0]): noneAdded = False
				# Add the string to the new window title.
				winTitle += nStr
		# If at least one tag was added, return the title, otherwise fall
		# back to the filename function.
		if (not noneAdded): return winTitle

	# Otherwise we want to use the filename (files name - extension)
	# Get the last item when split at '/'.  eg a/b/c.d -> c.d
	if (os.sep in file): file = file.split(os.sep)[-1]
	# Remove the file extenstion (wow, this is messy).
	if ('.' in file): file = file[:-(len(file.split('.')[-1]) + 1)]
	winTitle = file
	return winTitle

def tagType(file):
	## Gets a tag type for some specific tag types (from file extension).
	# Read the file extension.
	ext = None
	if ('.' in file): ext = file[-(len(file.split('.')[-1])):]
	# Import the tag functions.
	from mutagen.oggflac import OggFLAC
	from mutagen.oggspeex import OggSpeex
	from mutagen.oggtheora import OggTheora
	from mutagen.oggvorbis import OggVorbis
	# Make a dictionary for easy access to types.
	# TODO: Add OggTheora to ogg & ogv again, if it's no-longer slow.
	dic = { 'ogg' : [OggFLAC, OggSpeex, OggVorbis],
	        'ogv' : [OggFLAC, OggSpeex, OggVorbis],
	        'oga' : [OggFLAC, OggSpeex, OggVorbis] }
	# Return the tag type, otherwise return None (which will check everything)
	try:
		return dic[ext]
	except:
		return None
