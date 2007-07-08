#!/usr/bin/env python

import os, sys

origdir = os.getcwd()
os.chdir(sys.path[0])

os.system('intltool-extract --type="gettext/glade" ../src/gui/whaawmp.glade')
os.system('xgettext -k_ -kN_ -o messages.pot ../src/*.py ../src/gui/*.py ../src/gui/whaawmp.glade.h')

print 'messages.pot updated!'

if not (len(sys.argv) > 1): sys.exit(0)

if (sys.argv[1] == 'compile'):
	for x in os.listdir(os.getcwd()):
		if (x.endswith('.po')):
			lang = x[:len(x)-3]
			dest = os.path.join(lang, 'LC_MESSAGES')
			if (not os.path.exists(dest)):
				os.makedirs(dest)
			print 'Creating translation %s' % lang
			os.system('msgmerge -o - %s messages.pot | msgfmt -c -o %s/LC_MESSAGES/whaawmp.mo -' % (x, lang))
			
