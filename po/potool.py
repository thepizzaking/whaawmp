#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#  A tool to help localisations.
#  Copyright © 2007-2011, Jeff Bailes <thepizzaking@gmail.com>
#
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the Licence, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys

if ('-h' in sys.argv or '--help' in sys.argv):
	## If help is requested, print out this help list, then exit.
	print '''
A small script I wrote to help with tanlsations, (A lot of thanks goes to 
the developers of exaile and deluge, as I based this on their scripts).
Onto the commands:
	'./potool.py' by itself will update the messages.pot file (This will
		be done on all commands).
	'./potool.py po LANGCODE' will create LANGCODE.po file if it doesn't
		already exist, otherwise it will just update it.
		(Use ./potool.py po all to update all po files)
	'./potool.py compile' will compile all the language file and put them
		in locale/LANGCODE/LC_MESSAGES/ folders.
If you are producing a translation please use the launchpad tranlation
	service: http://translations.launchpad.net/whaawmp
Good luck, and happy translating.'''
	sys.exit(0)

# Change to the directory the script is in, so functions can be performed easier.
os.chdir(sys.path[0])

def updatePOT():
	## Update the 'messages.pot' file, this happens whenever the script is run.
	uiHeadersStr = ""
	for x in ['main', 'preferences']:
		# Extract strings from all gtkBuilder files.
		uiFile = '../ui/%s.ui' % x
		os.system('intltool-extract --type="gettext/glade" %s' % uiFile)
		uiHeadersStr = uiHeadersStr + ' %s.h' % uiFile
	# Merge it all together into the messages.pot file.
	os.system('xgettext -k_ -kN_ -o messages.pot ../src/*.py ../src/gui/*.py ../src/common/*.py %s' % uiHeadersStr)
	# Remove the unneeded *.ui.h files.
	os.system('rm %s' % uiHeadersStr)
	print 'messages.pot updated!'


def createUpdatePO(lang):
	## If 'po' was passed, we want to either create or update a .po file.
	lang = sys.argv[2]
	if (lang == 'all'):
		# If the language requested was 'all', we want to update all .po files.
		for x in os.listdir(os.getcwd()):
			if (x.endswith('.po')):
				# For all the .po files in the directory, call update on them.
				updatepo(x[:len(x)-3])
	elif (os.path.exists('%s.po' % (lang))):
		# Otherwise, if the .po file requested already exists, update it.
		updatepo(lang)
	else:
		# Finally, if it doesn't exist, copy the messages.pot file to lang.po.
		os.system('cp messages.pot %s.po' % (lang))
		print '%s.po created' % (lang)

def updatepo(lang):
	## A function which updates an existing translation file.
	# Merge the old file and the .pot file, then replace the old one with the
	# merged one.
	os.system('msgmerge %s.po messages.pot > tmp.po' % (lang))
	os.system('mv tmp.po %s.po' % lang)
	print '%s.po updated' % (lang)

def compilePO():
	## It was requested to compile the language files.
	for x in os.listdir(os.getcwd()):
		if (x.endswith('.po')):
			# For all the po files in the directory.
			lang = x[:len(x)-3]
			dest = os.path.join('locale', lang, 'LC_MESSAGES')
			if (not os.path.exists(dest)):
				# If the direcory 'lang/LC_MESSAGES' doesn't exist, create it.
				os.makedirs(dest)
			# Compile the file and put it in the 'lang/LC_MESSAGES' directory.
			print 'Creating translation %s' % lang
			os.system('msgmerge -o - %s messages.pot | msgfmt -c -o %s/whaawmp.mo -' % (x, dest))	

updatePOT()
## If no arguments were passed, exit, the messages.pot file has been updated.
if not (len(sys.argv) > 1): sys.exit(0)
if (sys.argv[1] == 'po' and len(sys.argv) > 2): createUpdatePO(sys.argv[2])
if (sys.argv[1] == 'compile'): compilePO()
