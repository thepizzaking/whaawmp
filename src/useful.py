#!/usr/bin/env python

#  A few useful functions for Whaaw! Media Player.
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

def nsTos(ns):
	## Converts nanoseconds to seconds.
	return ns / 1000000000

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
