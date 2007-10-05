#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  A building/installation script for Whaaw! Media Player.
#  Copyright © 2007, Jeff Bailes <thepizzaking@gmail.com>
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

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install_lib import install_lib
import distutils.dir_util
from distutils import cmd
import glob
import os

scripts = {'whaawmp' : 'whaawmp.py',
           'whaaw-thumbnailer' : 'thumbnailer.py'}

def replaceStr(file, orig, new):
	f = open(file, 'r')
	data = f.read()
	f.close()
	data = data.replace(orig, new)
	f = open(file, 'w')
	f.write(data)
	f.close()

class libInstall(install_lib):
	def run(self):
		root = getattr(self.get_finalized_command('install'), 'root')
		prefix = getattr(self.get_finalized_command('install'), 'prefix')
		libDir = getattr(self.get_finalized_command('build'), 'build_lib')
		# To fix the datadir location.
		filename = os.path.join(libDir, 'whaawmp', 'common', 'useful.py')
		datadir = os.path.join(prefix, 'share', 'whaawmp')
		replaceStr(filename, '@datadir@', datadir)
		# Install the locales.
		os.system('./po/potool.py compile')
		if (os.path.exists('po/locale')):
			distutils.dir_util.copy_tree('po/locale', ('%s%s/share/locale' % (root, prefix)))
		res = install_lib.run(self)
		replaceStr(filename, datadir, '@datadir@')
		return res

class dataInstall(install_data):
	def run(self):
		install_cmd = self.get_finalized_command('install')
		libDir = getattr(install_cmd, 'install_lib')
		if (self.root and libDir.startswith(self.root)):
			basedir = os.path.join(libDir[len(self.root):], 'whaawmp')
			if not (basedir.startswith('/')): basedir = '/' + basedir
		else:
			basedir = os.path.join(libDir, 'whaawmp')
		
		for x in scripts:
			f = open(x, 'w')
			f.write('#!/bin/sh\nexec python %s/%s "$@"' % (basedir, scripts[x]))
			f.close()
			os.system('chmod 755 %s' % x)
		return install_data.run(self)
		
data = [('share/whaawmp/glade', glob.glob('glade/*.glade')),
        ('share/whaawmp/images', glob.glob('images/*.svg')),
        ('share/pixmaps', ['images/whaawmp.svg']),
        ('share/applications', ['whaawmp.desktop']),
        ('share/thumbnailers', ['whaaw-thumbnailer.desktop']),
        ('bin', scripts.keys())]

setup(name="whaawmp", fullname="Whaaw! Media Player",
      version='0.2.3',
      description='Whaaw! Media Player',
      author='Jeff Bailes',
      author_email='thepizzaking@gmail.com',
      url='http://home.gna.org/whaawmp/',
      packages=['whaawmp','whaawmp.gui','whaawmp.common'],
      package_dir={'whaawmp': 'src'},
      data_files=data,
      cmdclass = {'install_lib' : libInstall,
                  'install_data' : dataInstall})
