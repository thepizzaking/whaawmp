#!/usr/bin/env python

#  A few gstreamer tools that I thought I could use.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import pygst
pygst.require('0.10')
import gst

def streamType(stream):
	## Returns the stream type as a string from a given stream.
	type = stream.get_property('type')
	types = { 0 : 'unknown',
	          1 : 'audio',
	          2 : 'video',
	          3 : 'text',
	          4 : 'element' }
	return types[type]
