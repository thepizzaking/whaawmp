# -*- coding: utf-8 -*-

#  The subtitle manager.
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

import os

from common.gstPlayer import player
from common.config import cfg
from common import useful
import gtk

class subMan():
	# A subtitle manager window.
	def destroy(self, widget=None, event=None):
		self.window.destroy()
	
	def autoSubsToggled(self, widget):
		# Set the automatic subtitles config option.
		cfg.set('video/autosub', widget.get_active())
	
	def subsExtsChanged(self, widget):
		# Change the automatically detected subtitles extensions.
		cfg.set('video/autosubexts', widget.get_text())
		
	def changeFont(self, widget):
		# Callback when the subtitle font is changed.
		font = widget.get_font_name()
		# Set the config option and apply the change to the player.
		cfg.set('video/subfont', font)
		player.setSubFont(font)
		
	
	def getCfg(self):
		# Get the config options and give it to the window.
		self.chkAutoSubs.set_active(cfg.getBool('video/autosub'))
		self.txtSubsExt.set_text(cfg.getStr('video/autosubexts'))
	
	def addSubs(self, widget):
		# Add subtitles to the current file from a file dialogue.
		dlg = gtk.FileChooserDialog(_("Choose a subtitle stream."), self.window,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		# Use the same folder as the last file opened.
		dlg.set_current_folder(useful.lastFolder)
		res = dlg.run()
		
		if (res == gtk.RESPONSE_OK) and (player.player.get_property('n-video') >= 1):
			# If the response was 'OK' and there is a video track get the filename.
			file = dlg.get_filename()
			# We need to restart the player so the subtitles work.
			#played = player.getPlayed()
			player.stop()
			# Reset everything.
			player.player.set_property('uri', player.uri)
			player.player.set_property('suburi', useful.filenameToUri(file))
			player.play()
			#player.seek(played)
		
		dlg.destroy()
	
	def __init__(self, parent):
		# The subtitle manager window.
		window = gtk.Window()
		window.set_title(_("Subtitle Manager"))
		window.set_transient_for(parent)
		window.set_destroy_with_parent(True)
		window.connect('delete-event', self.destroy)
		window.set_resizable(False)
		window.set_border_width(7)
		self.window = window
		vBox = gtk.VBox(spacing=7)
		window.add(vBox)
		# The automatic subtitles checkbox.
		chkAutoSubs = gtk.CheckButton(_("Automatic Subtitles"))
		chkAutoSubs.set_has_tooltip(True)
		chkAutoSubs.set_tooltip_text(_("Try to automatically find subtitles for each file."))
		chkAutoSubs.connect('toggled', self.autoSubsToggled)
		self.chkAutoSubs = chkAutoSubs
		vBox.pack_start(chkAutoSubs)
		hBox = gtk.HBox(spacing=7)
		vBox.pack_start(hBox)
		# The automatic subtitle extensions entry.
		lblSubsExt = gtk.Label(_("Subtitle file extensions"))
		hBox.pack_start(lblSubsExt)
		txtSubsExt = gtk.Entry()
		txtSubsExt.set_has_tooltip(True)
		txtSubsExt.set_tooltip_text(_("Extensions to use when automatically detecting subtitles.\nSepatare with commas."))
		txtSubsExt.connect('changed', self.subsExtsChanged)
		self.txtSubsExt = txtSubsExt
		hBox.pack_start(txtSubsExt)
		# The add subtitles to current stream button.
		btnAddSub = gtk.Button(_("Add subtitles to current stream"))
		img = gtk.Image()
		img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
		btnAddSub.set_image(img)
		btnAddSub.connect('clicked', self.addSubs)
		vBox.pack_start(btnAddSub)
		# Font selection.
		btnFont = gtk.FontButton(cfg.get('video/subfont'))
		btnFont.connect('font-set', self.changeFont)
		vBox.pack_start(btnFont)
		# A button box that contains the close button.
		btnBox = gtk.HButtonBox()
		btnBox.set_layout(gtk.BUTTONBOX_END)
		btnClose = gtk.Button('gtk-close')
		btnClose.set_use_stock(True)
		btnBox.pack_start(btnClose)
		btnClose.connect('clicked', self.destroy)
		vBox.pack_start(btnBox)
		# Do it all.
		self.getCfg()
		window.show_all()


def trySubs(file):
	# Trys to automatically set the subtitle track for a file.
	# Get rid of the file:// at the start (if it's there).
	if ('file://' in file): file = file[7:]
	# Rip off the files extension.
	(root, x) = os.path.splitext(file)
	for ext in cfg.getStr('video/autosubexts').split(','):
		# For all the extensions in the extensions list.
		subPath = '%s.%s' % (root, ext)
		if os.path.exists(subPath):
			# If the subtitle file exists DO IT!
			player.player.set_property('suburi', useful.filenameToUri(subPath))
			print _("Found subtitles stream %s" % subPath)
			return True
	
	return False
