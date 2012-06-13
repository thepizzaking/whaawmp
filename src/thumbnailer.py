#! /usr/bin/env python2
# -*- coding: utf-8 -*-

#  A video thumbnailer for use with whaawmp.
#  Copyright © 2007-2011, Jeff Bailes <thepizzaking@gmail.com>
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

__sName__ = 'whaaw-thumbnailer'

try:
	# Change the process name.
	import ctypes
	libc = ctypes.CDLL('libc.so.6')
	libc.prctl(15, __sName__, 0, 0)
except:
	pass

import sys, os
from optparse import OptionParser
import gettext
gettext.install('whaawmp', unicode=1)

# Check for help here, so gstreamer doesn't steal --help.
# Flag HELP as false.
HELP = False
for x in sys.argv:
	if x in [ '-h', '--help' ]:
		# For all arguments, if they're --help or -h, HELP is true, then
		# remove the argument.
		HELP = True
		sys.argv.remove(x)

import pygtk, pygst
pygtk.require('2.0')
pygst.require('0.10')
import gtk, gst

# The film strip svg icon. You can take this, dump it in an .svg file
# and view/edit with any svg viewer/editor
film_strip_svg='<?xml version="1.0" encoding="UTF-8" standalone="no"?> <!-- Created with Inkscape (http://www.inkscape.org/) --> <svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="1052.3622" height="744.09448" id="svg3126" version="1.1" inkscape:version="0.48.1 r9760" sodipodi:docname="film-strip2.svg"> <defs id="defs3128"> <linearGradient inkscape:collect="always" id="linearGradient4146"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150" /> </linearGradient> <linearGradient id="linearGradient3938"> <stop style="stop-color:#000000;stop-opacity:1;" offset="0" id="stop3940" /> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="1" id="stop3942" /> </linearGradient> <radialGradient inkscape:collect="always" xlink:href="#linearGradient4146" id="radialGradient4152" cx="22.216942" cy="344.42444" fx="22.216942" fy="344.42444" r="15" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-1012.8658)" gradientUnits="userSpaceOnUse" /> <radialGradient inkscape:collect="always" xlink:href="#linearGradient4146-8" id="radialGradient4152-1" cx="22.216942" cy="344.42444" fx="22.216942" fy="344.42444" r="15" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57961,-694.31262)" gradientUnits="userSpaceOnUse" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57961,-644.31261)" gradientUnits="userSpaceOnUse" id="radialGradient4171-5" xlink:href="#linearGradient4146-8-3" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57961,-594.31263)" gradientUnits="userSpaceOnUse" id="radialGradient4222-6" xlink:href="#linearGradient4146-8-3-0" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57961,-544.31263)" gradientUnits="userSpaceOnUse" id="radialGradient4256-6" xlink:href="#linearGradient4146-8-3-0-4" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57961,-494.31261)" gradientUnits="userSpaceOnUse" id="radialGradient4290-4" xlink:href="#linearGradient4146-8-3-0-4-8" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-444.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4324-1" xlink:href="#linearGradient4146-8-3-0-4-8-3" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-8" xlink:href="#linearGradient4146-8-3-0-4-8-3-4" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-4"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-5" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-2" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-80" xlink:href="#linearGradient4146-8-3-0-4-8-3-5" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-5"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-50" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-7" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-9" xlink:href="#linearGradient4146-8-3-0-4-8-3-0" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-0"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-6" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-0" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-6" xlink:href="#linearGradient4146-8-3-0-4-8-3-1" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-1"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-0" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-05" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-5" xlink:href="#linearGradient4146-8-3-0-4-8-3-7" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-7"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-06" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-4" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-50" xlink:href="#linearGradient4146-8-3-0-4-8-3-50" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-50"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-8" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-6" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-394.3126)" gradientUnits="userSpaceOnUse" id="radialGradient4358-0" xlink:href="#linearGradient4146-8-3-0-4-8-3-46" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-46"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-7" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-27" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(6.6326537,-0.04858221,0.02145399,3.0162962,-131.57962,-44.312622)" gradientUnits="userSpaceOnUse" id="radialGradient4392-27-2" xlink:href="#linearGradient4146-8-3-0-4-8-3-46-0" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-8-3-0-4-8-3-46-0"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-5-8-9-2-1-3-7-6" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-0-6-2-1-1-0-27-7" /> </linearGradient> <radialGradient inkscape:collect="always" xlink:href="#linearGradient4146-2" id="radialGradient4152-9" cx="22.216942" cy="344.42444" fx="22.216942" fy="344.42444" r="15" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-1012.8658)" gradientUnits="userSpaceOnUse" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-912.86583)" gradientUnits="userSpaceOnUse" id="radialGradient3170" xlink:href="#linearGradient4146-2" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-912.86583)" gradientUnits="userSpaceOnUse" id="radialGradient3170-3" xlink:href="#linearGradient4146-2-6" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204" xlink:href="#linearGradient4146-2-6" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204-5" xlink:href="#linearGradient4146-2-6-0" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6-0"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8-6" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0-4" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-712.86585)" gradientUnits="userSpaceOnUse" id="radialGradient3238" xlink:href="#linearGradient4146-2-6-0" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204-9" xlink:href="#linearGradient4146-2-6-08" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6-08"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8-1" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0-3" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-612.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3238-1" xlink:href="#linearGradient4146-2-6-08" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204-6" xlink:href="#linearGradient4146-2-6-9" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6-9"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8-3" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0-38" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-512.86584)" gradientUnits="userSpaceOnUse" id="radialGradient3238-0" xlink:href="#linearGradient4146-2-6-9" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204-8" xlink:href="#linearGradient4146-2-6-7" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6-7"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8-2" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0-8" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-412.86579)" gradientUnits="userSpaceOnUse" id="radialGradient3238-2" xlink:href="#linearGradient4146-2-6-7" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-812.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3204-3" xlink:href="#linearGradient4146-2-6-2" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-2-6-2"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-54-8-15" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-05-0-9" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-312.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3238-9" xlink:href="#linearGradient4146-2-6-2" inkscape:collect="always" /> <radialGradient inkscape:collect="always" xlink:href="#linearGradient4146-3" id="radialGradient4152-8" cx="22.216942" cy="344.42444" fx="22.216942" fy="344.42444" r="15" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-182.81146,-1012.8658)" gradientUnits="userSpaceOnUse" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359" xlink:href="#linearGradient4146-3" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-0" xlink:href="#linearGradient4146-3-4" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-4"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-8" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-7" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3116,-912.86584)" gradientUnits="userSpaceOnUse" id="radialGradient3393" xlink:href="#linearGradient4146-3-4" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-9" xlink:href="#linearGradient4146-3-3" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-3"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-9" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-2" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-812.86583)" gradientUnits="userSpaceOnUse" id="radialGradient3393-8" xlink:href="#linearGradient4146-3-3" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-8" xlink:href="#linearGradient4146-3-9" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-9"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-1" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-5" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-712.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3393-4" xlink:href="#linearGradient4146-3-9" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-2" xlink:href="#linearGradient4146-3-5" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-5"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-7" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-4" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-612.86582)" gradientUnits="userSpaceOnUse" id="radialGradient3393-9" xlink:href="#linearGradient4146-3-5" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-81" xlink:href="#linearGradient4146-3-99" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-99"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-78" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-25" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-412.86581)" gradientUnits="userSpaceOnUse" id="radialGradient3393-3" xlink:href="#linearGradient4146-3-99" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-02" xlink:href="#linearGradient4146-3-0" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-0"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-19" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-6" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-512.86582)" gradientUnits="userSpaceOnUse" id="radialGradient3393-2" xlink:href="#linearGradient4146-3-0" inkscape:collect="always" /> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-1012.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3359-20" xlink:href="#linearGradient4146-3-7" inkscape:collect="always" /> <linearGradient inkscape:collect="always" id="linearGradient4146-3-7"> <stop style="stop-color:#ffffff;stop-opacity:1;" offset="0" id="stop4148-3-3" /> <stop style="stop-color:#ffffff;stop-opacity:0;" offset="1" id="stop4150-3-1" /> </linearGradient> <radialGradient r="15" fy="344.42444" fx="22.216942" cy="344.42444" cx="22.216942" gradientTransform="matrix(9.2857152,-0.0633681,0.03003559,3.9342994,-1235.3115,-312.8658)" gradientUnits="userSpaceOnUse" id="radialGradient3393-1" xlink:href="#linearGradient4146-3-7" inkscape:collect="always" /> </defs> <sodipodi:namedview id="base" pagecolor="#ffffff" bordercolor="#666666" borderopacity="1.0" inkscape:pageopacity="0.0" inkscape:pageshadow="2" inkscape:zoom="0.7176508" inkscape:cx="526.18109" inkscape:cy="372.04724" inkscape:document-units="px" inkscape:current-layer="layer1" showgrid="false" showguides="true" inkscape:guide-bbox="true" inkscape:window-width="1280" inkscape:window-height="752" inkscape:window-x="0" inkscape:window-y="0" inkscape:window-maximized="1"> <inkscape:grid type="xygrid" id="grid4040" empspacing="5" visible="true" enabled="true" snapvisiblegridlinesonly="true" /> <sodipodi:guide orientation="1,0" position="-280,600" id="guide4144" /> </sodipodi:namedview> <metadata id="metadata3131"> <rdf:RDF> <cc:Work rdf:about=""> <dc:format>image/svg+xml</dc:format> <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage" /> <dc:title></dc:title> </cc:Work> </rdf:RDF> </metadata> <g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1" transform="translate(0,-308.2677)"> <rect style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3926" width="60" height="744.08502" x="0.00390625" y="308.27231" /> <rect style="fill:url(#radialGradient4152);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928" width="42" height="30" x="10.5" y="322.36218" rx="8.6656332" /> <rect style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3926-9" width="60" height="744.08496" x="-1051.9889" y="308.27234" transform="scale(-1,1)" /> <rect style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect4790" width="972.44373" height="4.8770242" x="39.712917" y="308.2677" /> <rect style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect4790-2" width="972.44373" height="4.8770242" x="39.822784" y="1047.4871" /> <rect style="fill:url(#radialGradient3170);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9" width="42" height="30" x="10.5" y="422.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3204);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2" width="42" height="30" x="10.5" y="522.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3238);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2-6" width="42" height="30" x="10.5" y="622.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3238-1);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2-1" width="42" height="30" x="10.5" y="722.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3238-0);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2-5" width="42" height="30" x="10.5" y="822.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3238-2);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2-9" width="42" height="30" x="10.5" y="922.36218" rx="8.6656332" /> <rect style="fill:url(#radialGradient3238-9);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-9-2-14" width="42" height="30" x="10.5" y="1022.3622" rx="8.6656332" /> <rect style="fill:url(#radialGradient3359);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8" width="42" height="30" x="-1042" y="322.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-0" width="42" height="30" x="-1042" y="422.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-8);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-3" width="42" height="30" x="-1042" y="522.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-4);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-9" width="42" height="30" x="-1042" y="622.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-9);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-94" width="42" height="30" x="-1042" y="722.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-3);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-4" width="42" height="30" x="-1042" y="922.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-2);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-1" width="42" height="30" x="-1042" y="822.36218" rx="8.6656332" transform="scale(-1,1)" /> <rect style="fill:url(#radialGradient3393-1);fill-opacity:1;fill-rule:nonzero;stroke:none" id="rect3928-8-90" width="42" height="30" x="-1042" y="1022.3622" rx="8.6656332" transform="scale(-1,1)" /> </g> </svg> '

class main:
	def __init__(self):
		# Flag that the player hasn't paused yet and we don't want to get the
		# thumbnail yet.
		self.pausedYet = False
		self.getThumb = False
		# Parser the command line options.
		self.parseOptions()
		#Create the player.
		self.createPlayer()
	
	
	def parseOptions(self):
		## Parses the command line options.
		# Create the parser, and set the usage.
		parser = OptionParser(usage="\n  " + __sName__ + _(" [options] -o output-file input-file"))
		# Add parser options:
		# Input file (can be an absolute or relative path).
		parser.add_option("-i", "--input", dest="input",
		                  default=None, metavar="FILE",
		                  help=_("The file to create the thumbnail of"))
		# The output file of the thumbnail.
		parser.add_option("-o", "--output", dest="output",
		                  default=None, metavar="FILE",
		                  help=_("The destination of the resulting thumbnail"))
		# The position in the video to get the thumbnail from.
		parser.add_option("-p", "--position", dest="pos",
		                  default=0.3, metavar="FRAC",
		                  help=_("The position (Fraction) to take the thumbnail from (default 0.3)"))
		# The output size.
		parser.add_option("-s", "--size", dest="size",
		                  default=None, metavar="SIZE",
		                  help=_("The destination size (in pixels)"))
		# Film strip option.
		parser.add_option("-f", "--film-strip",
		                  action="store_true", dest="filmstrip",
				  default=False,
				  help=_("Create a film strip overlay"))
		 
		if (HELP):
			# If help is requested print it, then exit.
			parser.print_help()
			sys.exit(0)
		# Parse the options.
		options, args = parser.parse_args()
		
		if (not options.output or (len(args) == 0 and not options.input)):
			# Either an input or output file wasn't defined, so we can't continue.
			print _("Sorry, an input and output file are required to be passed.")
			print _("See '%s --help' for details") % (__sName__)
			sys.exit(1)
		# Turn the position into a float.
		if (options.size): options.size = int(options.size)
		options.pos = float(options.pos)
		if (options.pos > 1 or options.pos < 0):
			# If the position is not between 0 and 1, default to 0.3.
			print _('The requested position must be between 0 and 1, using 0.3.')
			options.pos = 0.3
		if (not options.input):
			# If the URI and the input file wasn't defined, the input file
			# should be the first item in the args list.
			options.input = args[0]
		if ('://' not in options.input):
			# If the URI was not defined, get it from the input file.
			options.input = 'file://' + os.path.abspath(options.input)
		
		# Make the option accessable from anywhere.
		self.options = options
		
	
	def createPlayer(self):
		## Creates the player.
		# Actually create a player.
		self.player = gst.element_factory_make('playbin', 'player')
		
		# Create a new bin.
		bin = gst.Bin('video')
		# Create a new filter, then add it.
		filter = gst.element_factory_make('capsfilter', 'filter')
		bin.add(filter)
		# Set the capabilities of the filter.
		filter.set_property('caps', gst.Caps('video/x-raw-rgb, depth=24, bpp=24'))
		# Create a fakesink and add it to the bin.
		vSink = gst.element_factory_make('fakesink', 'vsink')
		bin.add(vSink)
	
		# if a film strip is going to be used, add the
		# appropriate elements to the bin. These include, in
		# turn:
		# ffmpegcolorspace -> rsvgoverlay -> ffmpegcolorspace 
		# and then connect the output of that to the filter.
		# Finally, add a ghostpad to the bin, so you can actually 
		# connect to it.
		try:
			if self.options.filmstrip:
				ffclsp1 = gst.element_factory_make('ffmpegcolorspace', 'ffclsp1')
				bin.add(ffclsp1)
				svg = gst.element_factory_make('rsvgoverlay', 'svg')
				svg.set_property('data', film_strip_svg)
				svg.set_property('fit-to-frame', True)
				bin.add(svg)
				ffclsp2 = gst.element_factory_make('ffmpegcolorspace', 'ffclsp2')
				bin.add(ffclsp2)
				# The first element in the bin in this case is
				# ffclsp1, so that's where the ghostpad
				# is added.
				ghostpad = gst.GhostPad("sink", ffclsp1.get_pad("sink"))
				gst.element_link_many(ffclsp1, svg, ffclsp2, filter)
			else:
				# When we don't ask for the film strip, the
				# first element in the bin is filter.
				ghostpad = gst.GhostPad("sink", filter.get_pad("sink"))
		# Catch the exception in case the rsvgoverlay gstreamer
		# plugin is not installed and a film strip is requested.
		# Just not add the film strip in that case.
		except gst.ElementNotFoundError:
				print _('WARNING: The rsvgoverlay gstreamer plugin is not installed. A film strip will not be added.')
				ghostpad = gst.GhostPad("sink", filter.get_pad("sink"))
		bin.add_pad(ghostpad)

		# Get the videosinks sink pad, and add a buffer probe to it.
		pad = vSink.get_pad("sink")
		pad.add_buffer_probe(self.onBufferProbe)
		
		# Link the filter and the video-sink
		gst.element_link_many(filter, vSink)
		# Set the player's video-sink to the newly created bin.
		self.player.set_property('video-sink', bin)
		
		# Get the player's bus, add signal watch, then connect it.
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.watchID = self.bus.connect("message", self.onMessage)
		
		# Set the URI of the input file to the file passed.
		self.player.set_property('uri', self.options.input)
		# Set the player's state to paused.
		self.player.set_state(gst.STATE_PAUSED)
	
	
	def onBufferProbe(self, pad, buffer):
		if (self.getThumb):
			# If we want to capture the thumbnail.
			caps = buffer.caps
			if (caps == None):
				# If caps was none, quit.
				print _('Stream returned no caps, exiting')
				sys.exit(6)
			# Read the width and height.
			filters = caps[0]
			w = filters["width"]
			h = filters["height"]
			# Create a pixbuf from the data.
			pixbuf = gtk.gdk.pixbuf_new_from_data(buffer.data, gtk.gdk.COLORSPACE_RGB, False, 8, w, h, w*3)
			# Scale the pixbuf to the requested size (if requested).
			if (self.options.size):
				if (w > h):
					newW = self.options.size
					newH = int(h / (float(w) / newW))
				else:
					newH = self.options.size
					newW = int(w / (float(h) / newH))
				### Use gtk.gdk.INTERP_BILINEAR if this is too slow.
				pixbuf = pixbuf.scale_simple(newW, newH, gtk.gdk.INTERP_HYPER)
			# Save the pixbuf as the file requested at the command line.
			pixbuf.save(self.options.output, 'png')
			# Quit.
			sys.exit(0)
		return True
	
	def onMessage(self, bus, message):
		if (message.type == gst.MESSAGE_ERROR):
			# If it was an error, print the error and quit.
			print _("An error occurred")
			print message.parse_error()[0]
			sys.exit(1)
		if (message.src == self.player):
			# Only continue if the player is the source.
			if (message.type == gst.MESSAGE_STATE_CHANGED):
				# If it's a state change event, parse the event.
				old, new, pending = message.parse_state_changed()
				if (new == gst.STATE_PAUSED and not self.pausedYet):
					# If this is the first pause.
					# Check that there is at least one video track.
					vTracks = 0
					for x in self.player.get_property('stream-info-value-array'):
						vTracks += (x.get_property('type') == 2)
					if (not vTracks):
						# If there are no video tracks, quit.
						print _("There are no video tracks in this stream, exiting.")
						sys.exit(4)
					# Try and get the duration, if we can't, quit with an error.
					try:
						dur = self.player.query_duration(gst.FORMAT_TIME)[0]
					except:
						print _("Duration unable to be read, exiting.")
						sys.exit(3)
					# Get the requested position in nanoseconds.
					pos = dur * self.options.pos
					# Flag that we want to get the thumbnail.
					self.getThumb = True
					# Seek to the new position.
					res = self.player.seek(1.0, gst.FORMAT_TIME,
					                       gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
					                       gst.SEEK_TYPE_SET, pos,
					                       gst.SEEK_TYPE_NONE, 0)
					if (not res):
						# If the seek failed, quit with an error.
						print _("Unable to seek to requested position, exiting.")
						sys.exit(5)
					# Flag that the player has been paused.
					self.pausedYet = True
	
	



main()
# Start the main loop.
gtk.main()
