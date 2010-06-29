#!/usr/bin/env python

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
	
	def create_window(self):
		window = gtk.Window()
		window.set_title('Converter')
		window.connect('destroy', self.quit)
		main_box = gtk.VBox()
		window.add(main_box)
		file_select = gtk.FileChooserButton("Source File")
		main_box.pack_start(file_select)
		encoder_box = gtk.HBox()
		main_box.pack_start(encoder_box)
		video_box = gtk.VBox()
		audio_box = gtk.VBox()
		encoder_box.pack_start(video_box)
		encoder_box.pack_start(gtk.VSeparator())
		encoder_box.pack_start(audio_box)
		video_box.pack_start(gtk.Label("Video Encoder"))
		audio_box.pack_start(gtk.Label("Audio Encoder"))
		self.fill_encoders(video_box, video_encoders)
		self.fill_encoders(audio_box, audio_encoders)
		main_box.pack_start(gtk.HSeparator())
		muxer_box = gtk.VBox()
		main_box.pack_start(muxer_box)
		muxer_box.pack_start(gtk.Label("Container Format"))
		self.fill_encoders(muxer_box, muxers)
		start_button = gtk.Button('Start')
		start_button.set_sensitive(False)
		main_box.pack_start(start_button)
		progress = gtk.ProgressBar()
		main_box.pack_start(progress)
		window.show_all()
	
	def __init__(self):
		self.create_window()
		gtk.main()

main()
