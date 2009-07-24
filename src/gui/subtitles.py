# -*- coding: utf-8 -*-

#  The subtitle manager.
#  Copyright © 2007-2009, Jeff Bailes <thepizzaking@gmail.com>
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

from common.gstPlayer import player
from common.config import cfg
from common import useful
import gtk

class subMan():
	# A subtitle manager window.
	def destroy(self, widget=None, event=None):
		self.window.destroy()
	
	def autoSubsToggled(self, widget):
		cfg.set('video/autosub', widget.get_active())
	
	def subsExtsChanged(self, widget):
		cfg.set('video/autosubexts', widget.get_text())
	
	def getCfg(self):
		self.chkAutoSubs.set_active(cfg.getBool('video/autosub'))
		self.txtSubsExt.set_text(cfg.getStr('video/autosubexts'))
	
	def addSubs(self, widget):
		dlg = gtk.FileChooserDialog(_("Choose a subtitle stream."), self.window,
		                  buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dlg.set_current_folder(useful.lastFolder)
		res = dlg.run()
		if (res == gtk.RESPONSE_OK):
			file = dlg.get_filename()
			played = player.getPlayed()
			player.stop()
			player.player.set_property('uri', player.uri)
			player.player.set_property('suburi', useful.filenameToUri(file))
			player.play()
			#player.seek(played)
		
		dlg.destroy()
	
	def __init__(self):
		window = gtk.Window()
		window.set_title(_("Subtitle Manager"))
		window.connect('delete-event', self.destroy)
		self.window = window
		vBox = gtk.VBox()
		window.add(vBox)
		chkAutoSubs = gtk.CheckButton(_("Automatic Subtitles"))
		chkAutoSubs.set_has_tooltip(True)
		chkAutoSubs.set_tooltip_text(_("Try to automatically find subtitles for each file."))
		chkAutoSubs.connect('toggled', self.autoSubsToggled)
		self.chkAutoSubs = chkAutoSubs
		vBox.pack_start(chkAutoSubs)
		hBox = gtk.HBox()
		vBox.pack_start(hBox)
		lblSubsExt = gtk.Label(_("Subtitle file extensions"))
		hBox.pack_start(lblSubsExt)
		txtSubsExt = gtk.Entry()
		txtSubsExt.set_has_tooltip(True)
		txtSubsExt.set_tooltip_text(_("Extensions to use when automatically detecting subtitles.\nSepatare with commas."))
		txtSubsExt.connect('changed', self.subsExtsChanged)
		self.txtSubsExt = txtSubsExt
		hBox.pack_start(txtSubsExt)
		btnAddSub = gtk.Button(_("Add subtitles to current stream"))
		img = gtk.Image()
		img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
		btnAddSub.set_image(img)
		btnAddSub.connect('clicked', self.addSubs)
		vBox.pack_start(btnAddSub)
		btnClose = gtk.Button('gtk-close')
		btnClose.set_use_stock(True)
		btnClose.connect('clicked', self.destroy)
		vBox.pack_start(btnClose)
		self.getCfg()
		window.show_all()
