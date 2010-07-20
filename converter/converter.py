#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Whaaw! Media Converter for transcoding media files.
#  Copyright © 2010, Jeff Bailes <thepizzaking@gmail.com>
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
import gobject
gobject.threads_init()
import pygtk, pygst
pygtk.require('2.0')
pygst.require('0.10')
import gtk, gst
from plugin_list import audio_encoders, video_encoders, muxers

class main:
	multipass_mode = None
	
	def quit(self, widget=None):
		gtk.main_quit()
	
	def fill_encoders(self, box, encoders):
		combobox = gtk.combo_box_new_text()
		combobox.append_text("None")
		combobox.set_active(0)
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
		self.vid_enc_cmb.connect("changed", self.video_enc_changed)
		self.aud_enc_cmb.connect("changed", self.audio_enc_changed)
		self.multipass_tick = gtk.CheckButton("Multipass")
		self.multipass_tick.set_sensitive(False)
		video_box.pack_start(self.multipass_tick)
		main_box.pack_start(gtk.HSeparator())
		muxer_box = gtk.VBox()
		main_box.pack_start(muxer_box)
		muxer_box.pack_start(gtk.Label("Container Format"))
		self.mux_cmb = self.fill_encoders(muxer_box, muxers)
		button_box = gtk.HBox()
		main_box.pack_start(button_box)
		start_button = gtk.ToggleButton('Start')
		#start_button.set_sensitive(False)
		start_button.connect('toggled', self.on_start_toggle)
		button_box.pack_start(start_button)
		self.cancel_button = gtk.Button('Cancel')
		self.cancel_button.connect('clicked', self.cancel_button_pressed)
		self.cancel_button.set_sensitive(False)
		button_box.pack_start(self.cancel_button)
		self.progress_bar = gtk.ProgressBar()
		main_box.pack_start(self.progress_bar)
		window.show_all()
		self.window = window
		self.start_button = start_button
	
	def video_enc_changed(self, widget):
		encoder = widget.get_active_text()
		self.multipass_tick.set_active(False)
		self.multipass_tick.set_sensitive('multipass' in video_encoders[encoder].keys())
	
	def audio_enc_changed(self, widget):
		pass
	
	def on_start_toggle(self, widget):
		if (widget.get_active()):
			try:
				state = self.pipe.get_state(timeout=200*gst.MSECOND)[1]
			except AttributeError:
				state = gst.STATE_READY
			
			if (state in (gst.STATE_NULL, gst.STATE_READY)):
				if self.multipass_tick.get_active():
					self.first_pass()
				else:
					self.transcode()
				widget.set_label('Pause')
				self.cancel_button.set_sensitive(True)
			elif (state == gst.STATE_PAUSED):
				self.pipe.set_state(gst.STATE_PLAYING)
				widget.set_label('Pause')
		else:
			self.pipe.set_state(gst.STATE_PAUSED)
			widget.set_label('Resume')
	
	def cancel_button_pressed(self, widget):
		dlg = gtk.MessageDialog(self.window, 0, gtk.MESSAGE_QUESTION,
		                        gtk.BUTTONS_YES_NO,
		                        "Are you sure you want to cancel the current transcode?")
		res = dlg.run()
		dlg.destroy()
		if (res == gtk.RESPONSE_YES):
			self.stop_transcode()
	
	def stop_transcode(self):
		try:
			self.pipe.set_state(gst.STATE_READY)
			self.start_button.set_active(False)
			self.start_button.set_label('Start')
			gobject.source_remove(self.progress_timer)
			self.progress_update(0)
			self.cancel_button.set_sensitive(False)
			self.pipe.set_state(gst.STATE_NULL)
		except AttributeError:
			pass
	
	def first_pass(self):
		self.multipass_mode = 1
		source = self.file_select.get_filename()
		
		video_encoder_name = self.vid_enc_cmb.get_active_text()
		muxer_name = self.mux_cmb.get_active_text()
		
		if (muxer_name == "None"):
			dlg = gtk.MessageDialog(self.window, 0, gtk.MESSAGE_INFO,
			                        gtk.BUTTONS_OK, "You should probably choose a Container Format")
			dlg.run()
			dlg.destroy()
			return

		if (video_encoder_name != "None"):
			video_encoder = video_encoders[video_encoder_name]['plugin']
		else:
			video_encoder = None

		self.pipe = gst.Pipeline()
		
		filesrc = gst.element_factory_make('filesrc')
		filesrc.set_property('location', source)
		
		decoder = gst.element_factory_make('decodebin2')
		decoder.connect('pad-added', self.on_dynamic_pad)
		self.pipe.add(filesrc, decoder)
		filesrc.link(decoder)
		multipass_info = video_encoders[video_encoder_name]['multipass']
		
		self.audio_queue = None
		
		if video_encoder:
			self.video_queue = gst.element_factory_make('queue')
			colourspace = gst.element_factory_make('ffmpegcolorspace')
			videoencode = gst.element_factory_make(video_encoder)
			videoencode.set_property(multipass_info[0], multipass_info[2])
		else:
			## FIXME: probably want to error here.
			return
		
		extension = muxers[muxer_name]['extension']
		
		videoencode.set_property(multipass_info[1], '%s.%s.multipass_cache' % (source, extension))
		sink = gst.element_factory_make('fakesink')
		
		if video_encoder:
			self.pipe.add(self.video_queue, colourspace, videoencode, sink)
			gst.element_link_many(self.video_queue, colourspace, videoencode, sink)
		
		bus = self.pipe.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.on_pipe_message)
		self.pipe.set_state(gst.STATE_PLAYING)
		self.progress_timer = gobject.timeout_add_seconds(1, self.progress_update)
	
	def transcode(self):
		source = self.file_select.get_filename()
		
		video_encoder_name = self.vid_enc_cmb.get_active_text()
		audio_encoder_name = self.aud_enc_cmb.get_active_text()
		muxer_name = self.mux_cmb.get_active_text()
		
		if (muxer_name == "None"):
			dlg = gtk.MessageDialog(self.window, 0, gtk.MESSAGE_INFO,
			                        gtk.BUTTONS_OK, "You should probably choose a Container Format")
			dlg.run()
			dlg.destroy()
			return
		
		if (video_encoder_name != "None"):
			video_encoder = video_encoders[video_encoder_name]['plugin']
		else:
			video_encoder = None
		if (audio_encoder_name != "None"):
			audio_encoder = audio_encoders[audio_encoder_name]['plugin']
		else:
			audio_encoder = None
		# Already checked if muxer_name was "None".
		muxer = muxers[muxer_name]['plugin']
		
		self.pipe = gst.Pipeline()
		
		filesrc = gst.element_factory_make('filesrc')
		filesrc.set_property('location', source)
		
		decoder = gst.element_factory_make('decodebin2')
		decoder.connect('pad-added', self.on_dynamic_pad)
		self.pipe.add(filesrc, decoder)
		filesrc.link(decoder)
		
		if audio_encoder:
			self.audio_queue = gst.element_factory_make('queue')
			audioconvert = gst.element_factory_make('audioconvert')
			audioencode = gst.element_factory_make(audio_encoder)
		else:
			self.audio_queue = None
		
		if video_encoder:
			self.video_queue = gst.element_factory_make('queue')
			colourspace = gst.element_factory_make('ffmpegcolorspace')
			videoencode = gst.element_factory_make(video_encoder)
		else:
			self.video_queue = None
		
		mux = gst.element_factory_make(muxer)
		
		if (audio_encoder and not video_encoder and ('audio_extension' in muxers[muxer_name].keys())):
			# If we're only encoding audio, use the audio only extension.
			extension = muxers[muxer_name]['audio_extension']
		else:
			extension = muxers[muxer_name]['extension']
			
		if self.multipass_tick.get_active() and self.multipass_mode == 2:
			multipass_info = video_encoders[video_encoder_name]['multipass']
			videoencode.set_property(multipass_info[0], multipass_info[3])
			videoencode.set_property(multipass_info[1], '%s.%s.multipass_cache' % (source, extension))
		
		filesink = gst.element_factory_make('filesink')
		filesink.set_property('location', '%s.%s' % (source, extension))
		
		self.pipe.add(mux)
		if audio_encoder:
			self.pipe.add(self.audio_queue, audioconvert, audioencode)
			gst.element_link_many(self.audio_queue, audioconvert, audioencode, mux)
		if video_encoder:
			self.pipe.add(self.video_queue, colourspace, videoencode)
			gst.element_link_many(self.video_queue, colourspace, videoencode, mux)
		
		self.pipe.add(filesink)
		mux.link(filesink)
		
		bus = self.pipe.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.on_pipe_message)
		self.pipe.set_state(gst.STATE_PLAYING)
		self.progress_timer = gobject.timeout_add_seconds(1, self.progress_update)
	
	def on_pipe_message(self, bus, message):
		if (message.type == gst.MESSAGE_EOS):
			self.stop_transcode()
			if (self.multipass_tick.get_active() and self.multipass_mode == 1):
				self.multipass_mode = 2
				self.transcode()
			else:
				dlg = gtk.MessageDialog(self.window, 0, gtk.MESSAGE_INFO,
										gtk.BUTTONS_OK, "Transcode complete")
				dlg.run()
				dlg.destroy()
				self.multipass_mode = None
	
	def progress_update(self, frac=None):
		if (frac is None):
			try:
				duration = self.pipe.query_duration(gst.FORMAT_TIME)[0]
			except:
				duration = 0
			try:
				position = self.pipe.query_position(gst.FORMAT_TIME)[0]
			except:
				position = 0
		
		if (frac is not None or duration > 0):
			fraction = frac if (frac is not None) else (position / duration)
			self.progress_bar.set_fraction(fraction)
			self.progress_bar.set_text(str(fraction))
		
		return True
			
	
	def on_dynamic_pad(self, source, pad):
		# Check if it's an audio or video stream (or neither).
		pad_type = 'video' if str(pad.get_caps()[0].get_name()).startswith('video') else 'audio'
		audio_pad = video_pad = None
		if self.video_queue: video_pad = self.video_queue.get_compatible_pad(pad)
		if self.audio_queue: audio_pad = self.audio_queue.get_compatible_pad(pad)
		# I originally didn't use the pad_type check, but gstreamer
		# believes it can link a video pad to an audio pad.
		if (pad_type == 'video' and video_pad):
			pad.link(video_pad)
		elif (pad_type == 'audio' and audio_pad):
			pad.link(audio_pad)
	
	def __init__(self):
		self.create_window()
		gtk.main()

main()
