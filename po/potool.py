#!/usr/bin/env python

import os, sys

origdir = os.getcwd()
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
			
