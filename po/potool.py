#!/usr/bin/env python

# Configuration Backend
# Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
#
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
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
	print '''
A small script I wrote to help with tanlsations, (A lot of thanks goes to 
the developers of exaile and deluge, as I based this on their scripts).
Onto the commands:
	'./potool.py' by itself will update the messages.pot file (This will
		be done on all commands).
	'./potool.py po LANGCODE' will create LANGCODE.po file if it doesn't
		already exist, otherwise it will just update it.
	'./potool.py compile' will compile all the language file and put them
		in LANGCODE/LC_MESSAGES/ folders.
Once you finish a translation, add them to the task manager here:
	http://gna.org/task/?group=whaawmp
Good luck, and happy translating.'''
	sys.exit(0)

os.chdir(sys.path[0])


os.system('intltool-extract --type="gettext/glade" ../src/gui/whaawmp.glade')
os.system('xgettext -k_ -kN_ -o messages.pot ../src/*.py ../src/gui/*.py ../src/gui/whaawmp.glade.h')

print 'messages.pot updated!'

if not (len(sys.argv) > 1): sys.exit(0)

if (sys.argv[1] == 'po' and len(sys.argv) > 2):
	if (os.path.exists('%s.po' % (sys.argv[2]))):
		os.system('msgmerge %s.po messages.pot > tmp.po' % (sys.argv[2]))
		os.system('mv tmp.po %s.po' % sys.argv[2])
		print '%s.po updated' % (sys.argv[2])
	else:
		os.system('cp messages.pot %s.po' % (sys.argv[2]))
		print '%s.po created' % (sys.argv[2])


if (sys.argv[1] == 'compile'):
	for x in os.listdir(os.getcwd()):
		if (x.endswith('.po')):
			lang = x[:len(x)-3]
			dest = os.path.join(lang, 'LC_MESSAGES')
			if (not os.path.exists(dest)):
				os.makedirs(dest)
			print 'Creating translation %s' % lang
			os.system('msgmerge -o - %s messages.pot | msgfmt -c -o %s/LC_MESSAGES/whaawmp.mo -' % (x, lang))
			
