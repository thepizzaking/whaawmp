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


def getTags(file):
	# Try and return the dictionary of tags.
	try:
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
	### Fix this so it's not really slow with videos.
	if avail:
		tags = getTags(file)
		# Get the first tag from title, and artist. (configuration maybe in the future).
		title = getSTag(tags, 'title')
		if (title):
			artist = getSTag(tags, 'artist')
			# If title exists, we use metadata, add artist to the front if it exists too.
			if (artist): winTitle += artist + ' - '
			winTitle += title
			return winTitle

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
	dic = { 'ogg' : [OggFLAC, OggSpeex, OggTheora, OggVorbis],
	        'ogv' : [OggTheora],
	        'oga' : [OggFLAC, OggSpeex, OggVorbis] }
	# Return the tag type, otherwise return None (which will check everything)
	try:
		return dic[ext]
	except:
		return None
