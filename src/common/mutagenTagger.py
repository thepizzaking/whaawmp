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
except ImportError:
	# If it fails, print an error message.
	print _("Mutagen not available, all tagging fetures will be unavailable")
	avail = False

import useful
from common.config import cfg

tagDic = {}

def getTags(file):
	# Turn it into a URI.
	if (not file.startswith("file://")): file = "file://" + os.path.abspath(file)
	try:
		# Try to get the tags from a dictionary cache.
		return tagDic[file]
	except KeyError:
		nonURI = file[7:]
		try:
			# If they weren't in the cache, try to get the tags through mutagen.
			tags = mutagen.File(nonURI, tagType(nonURI))
		except:
			# If that fails too, just use an empty dictionary.
			tags = {}
		# Save the tags to the dictionary and return them.
		tagDic[file] = tags
		return tags


def getTag(file, tag):
	try:
		return getTags(file)[tag]
	except:
		return []

def getSTag(file, tag):
	## Gets a single tag.
	# Get the list of tags.
	tagsi = getTag(file, tag)
	# If it's empty, return None.
	if (tagsi == []): return None
	# Otherwise, return the first item.
	return tagsi[0]

def getDispTitle(file):
	## Gets the (window) title to be displayed from Tags / filename.
	# If no file was passed, return an empty string. 
	if (not file): return ""
	# Initialise the winTitle to empty.
	winTitle = ""
	# If the tagger is available.
	if avail:
		# Flag that no tags have been added.
		noneAdded = True
		for x in useful.tagsToTuple(cfg.getStr('gui/tagsyntax')):
			# For all the items in the list produced by tagsToTuple.
			# New string = the associated tag if it's a tag, otherwise just the string.
			nStr = getSTag(file, x[1]) if (x[0]) else x[1]
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
