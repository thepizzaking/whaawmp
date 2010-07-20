# -*- coding: utf-8 -*-

#  Whaaw! Media Converter plugin list.
#  Copyright © 2007-2010, Jeff Bailes <thepizzaking@gmail.com>
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

audio_encoders = {
                  'Vorbis' :
                   {
                    'plugin' : 'vorbisenc'
                   },
                  'Lame (mp3)' :
                   {
                    'plugin' : 'lame'
                   }
                 }

video_encoders = {
                  'VP8' :
                   {
                    'plugin' : 'vp8enc',
                    'multipass' : ('multipass-mode', 'multipass-cache-file', 1, 2),
                    'quality' : 'quality'
                   },
                  'Theora' :
                   {
                    'plugin' : 'theoraenc'
                   },
                  'Dirac' :
                   {
                    'plugin' : 'schroenc'
                   },
                  'x264' :
                   {
                    'plugin' : 'x264enc'
                   },
                  'xvid' :
                   {
                    'plugin' : 'xvidenc'
                   }
                  }

muxers = {
          'Matroska' :
           {
            'plugin' : 'matroskamux',
            'extension' : 'mkv',
            'audio_extension' : 'mka'
           },
          'OGG' :
           {
            'plugin' : 'oggmux',
            'extension' : 'ogv',
            'audio_extension' : 'oga'
           },
          'AVI' :
           {
            'plugin' : 'avimux',
            'extension' : 'avi'
           },
          'MPEG TS' :
           {
            'plugin' : 'mpegtsmux',
            'extension' : 'mpeg'
           },
          'MPEG PS' :
           {
            'plugin' : 'mpegpsmux',
            'extension' : 'mpeg'
           }
          }
