#!/usr/bin/env python

#  A few useful lists.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>.
#       This file is part of Whaaw! Media Player (whaawmp)
#
#       whaawmp is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       whaawmp is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.


## The mime type list of compatable files, for open dialogue.
compatFiles = ['application/ogg', 'application/ram', 'application/smil',
               'application/vnd.rn-realmedia', 'application/x-extension-m4a',
               'application/x-extension-mp4', 'application/x-flac',
               'application/x-flash-video', 'application/x-matroska',
               'application/x-ogg', 'application/x-quicktime-media-link',
               'application/x-quicktimeplayer', 'application/x-shockwave-flash',
               'application/x-shorten', 'application/x-smil', 'application/xspf+xml',
               'audio/3gpp', 'audio/ac3', 'audio/AMR', 'audio/AMR-WB', 'audio/basic',
               'audio/mp4', 'audio/mpeg', 'audio/mpegurl', 'audio/vnd.rn-realaudio',
               'audio/x-ape', 'audio/x-flac', 'audio/x-it', 'audio/x-m4a', 
               'audio/x-matroska', 'audio/x-mod', 'audio/x-mp3', 'audio/x-mpeg',
               'audio/x-mpegurl', 'audio/x-ms-asf', 'audio/x-ms-asx', 'audio/x-ms-wax',
               'audio/x-ms-wma', 'audio/x-musepack', 'audio/x-pn-aiff', 'audio/x-pn-au',
               'audio/x-pn-realaudio', 'audio/x-pn-realaudio-plugin', 'audio/x-pn-wav',
               'audio/x-pn-windows-acm', 'audio/x-realaudio', 'audio/x-real-audio',
               'audio/x-scpls', 'audio/x-tta', 'audio/x-wav', 'audio/x-wav',
               'audio/x-wavpack', 'image/vnd.rn-realpix', 'image/x-pict', 'misc/ultravox',
               'text/google-video-pointer', 'text/x-google-video-pointer', 'video/3gpp',
               'video/dv', 'video/fli', 'video/flv', 'video/mp4', 'video/mp4v-es',
               'video/mpeg', 'video/msvideo', 'video/quicktime', 'video/vivo',
               'video/vnd.divx', 'video/vnd.rn-realvideo', 'video/vnd.vivo', 'video/x-anim',
               'video/x-avi', 'video/x-flc', 'video/x-fli', 'video/x-flic', 'video/x-m4v',
               'video/x-matroska', 'video/x-mpeg', 'video/x-ms-asf', 'video/x-msvideo',
               'video/x-ms-wm', 'video/x-ms-wmv', 'video/x-ms-wmx', 'video/x-ms-wvx',
               'video/x-nsv', 'video/x-ogm+ogg', 'video/x-theora+ogg', 'text/uri-list']


## The widgets that are normally hidden.
hiddenNormalWidgets = ['btnLeaveFullscreen']

## A list of widgets to hide on fullscreen.
hiddenFSWidgets = ['menubar', 'hboxTop', 'hboxControl', 'lblNowPlaying', 'btnLeaveFullscreen']

## The list of widgets to reshow when the mouse is moved (fullscreen).
fsShowWMouse = ['hboxTop', 'hboxControl', 'lblNowPlaying', 'btnLeaveFullscreen']


## A dicrtionary with all the default options.
defaultOptions = { 'video/brightness' : 0,
                   'video/contrast' : 0,
                   'video/hue' : 0,
                   'video/saturation' : 0,
                   'video/force-aspect-ratio' : True,
                   'video/videosink' : 'default',
                   'gui/mousehidetimeout' : 2000,
                   'gui/instantseek' : False,
                   'gui/volumescrollchange' : 5.0,
                   'gui/showtimeremaining' : False,
                   'gui/enablevisualisation' : True,
                   'gui/hidevideowindow' : True,
                   'gui/iconsize' : 1,
                   'audio/mute' : False,
                   'audio/volume' : 75,
                   'audio/audiosink' : 'default',
                   'misc/disablexscreensaver' : True }


## Some gstreamer lists.
## A list of gstreamer list types (in order too!).
gstStreamType = [ 'unknown', 'audio', 'video', 'text', 'element' ]

## A list of video-sinks, (in order of preference).
vsinkTypes = [ 'xvimagesink', 'ximagesink', 'glimagesink', 'fakesink' ]

## Lists of video sinks which support colour and aspect settings.
vsinkColour = ['xvimagesink']
vsinkAspect = ['xvimagesink', 'ximagesink']

## Available colour settings (Remember to use .lower() if lowercase required.
colourSettings = [ 'Brightness', 'Contrast', 'Hue', 'Saturation' ]
