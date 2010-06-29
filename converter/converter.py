#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Whaaw! Media Converter for transcoding media files.
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

'''http://pygstdocs.berlios.de/pygst-tutorial/pipeline.html for some useful looking code'''

from __future__ import print_function
from __future__ import division
import pygtk, pygst
pygtk.require('2.0')
pygst.require('0.10')
import gtk, gobject, gst
from plugin_list import audio_encoders, video_encoders, muxers

class main:
	def quit(self, widget=None):
		gtk.main_quit()
	
	def fill_encoders(self, box, encoders):
		combobox = gtk.combo_box_new_text()
		for x in encoders.keys():
			combobox.append_text(x)
		box.pack_start(combobox)
		return combobox
	
	def create_window(self):
		window = gtk.Window()
		window.set_title('Converter')
		window.connect('destroy', self.quit)
		main_box = gtk.VBox()
		window.add(main_box)
		self.file_select = gtk.FileChooserButton("Source File")
		main_box.pack_start(self.file_select)
		encoder_box = gtk.HBox()
		main_box.pack_start(encoder_box)
		video_box = gtk.VBox()
		audio_box = gtk.VBox()
		encoder_box.pack_start(video_box)
		encoder_box.pack_start(gtk.VSeparator())
		encoder_box.pack_start(audio_box)
		video_box.pack_start(gtk.Label("Video Encoder"))
		audio_box.pack_start(gtk.Label("Audio Encoder"))
		self.vid_enc_cmb = self.fill_encoders(video_box, video_encoders)
		self.aud_enc_cmb = self.fill_encoders(audio_box, audio_encoders)
		main_box.pack_start(gtk.HSeparator())
		muxer_box = gtk.VBox()
		main_box.pack_start(muxer_box)
		muxer_box.pack_start(gtk.Label("Container Format"))
		self.mux_cmb = self.fill_encoders(muxer_box, muxers)
		start_button = gtk.Button('Start')
		#start_button.set_sensitive(False)
		start_button.connect('clicked', self.transcode)
		main_box.pack_start(start_button)
		progress = gtk.ProgressBar()
		main_box.pack_start(progress)
		window.show_all()
	
	def transcode(self, widget=None):
		source = self.file_select.get_filename()
		
		video_encoder_name = self.vid_enc_cmb.get_active_text()
		audio_encoder_name = self.aud_enc_cmb.get_active_text()
		muxer_name = self.mux_cmb.get_active_text()
		
		video_encoder = video_encoders[video_encoder_name]['plugin']
		audio_encoder = audio_encoders[audio_encoder_name]['plugin']
		muxer = muxers[muxer_name]['plugin']
		
		self.pipe = gst.Pipeline('pipeline')
		
		self.filesrc = gst.element_factory_make('filesrc', 'source')
		self.filesrc.set_property('location', source)
		
		self.decoder = gst.element_factory_make('decodebin2', 'decoder')
		self.decoder.connect('new-decoded-pad', self.on_dynamic_pad)
		self.pipe.add(self.filesrc, self.decoder)
		self.filesrc.link(self.decoder)
		
		self.audioconvert = gst.element_factory_make('audioconvert', 'audioconvert')
		self.audioencode = gst.element_factory_make(audio_encoder, 'audioencode')
		self.mux = gst.element_factory_make(muxer, 'mux')
		
		self.filesink = gst.element_factory_make('filesink', 'sink')
		self.filesink.set_property('location', '%s.%s' % (source, muxers[muxer_name]['extension']))
		
		self.pipe.add(self.audioconvert, self.audioencode, self.mux, self.filesink)
		gst.element_link_many(self.audioconvert, self.audioencode, self.mux, self.filesink)
		
		self.pipe.set_state(gst.STATE_PLAYING)
	
	def on_dynamic_pad(self, dbin, pad, islast):
		# See if it's an audio stream.
		audio_pad = self.audioconvert.get_compatible_pad(pad)
		if audio_pad:
			pad.link(audio_pad)
	
	def __init__(self):
		self.create_window()
		gtk.main()

main()
