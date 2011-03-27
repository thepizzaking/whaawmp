#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#  A building/installation script for Whaaw! Media Player.
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

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install_lib import install_lib
import distutils.dir_util
from distutils import cmd
import glob
import sys, os

# A dictionary for bash scripts and their destination python files.
scripts = {'whaawmp' : 'whaawmp.py',
           'whaaw-thumbnailer' : 'thumbnailer.py'}

def replaceStr(file, orig, new):
	## A function to replace a string with a new string in a given file.
	# Open, read then close the file.
	f = open(file, 'r')
	data = f.read()
	f.close()
	# Replace the string in the data which was read.
	data = data.replace(orig, new)
	# Write the new data back into the file.
	f = open(file, 'w')
	f.write(data)
	f.close()

class libInstall(install_lib):
	## A class to extend the installation of libraries.
	def run(self):
		# Get the follwing paths.
		root = getattr(self.get_finalized_command('install'), 'root')
		prefix = getattr(self.get_finalized_command('install'), 'prefix')
		libDir = getattr(self.get_finalized_command('build'), 'build_lib')
		# To fix the datadir location in useful.py.
		filename = os.path.join(libDir, 'whaawmp', 'common', 'useful.py')
		datadir = os.path.join(prefix, 'share', 'whaawmp')
		replaceStr(filename, '@datadir@', datadir)
		# Install the locales, first compile them, then copy them over.
		os.system('%s po/potool.py compile' % sys.executable)
		if (os.path.exists('po/locale')):
			distutils.dir_util.copy_tree('po/locale', ('%s%s/share/locale' % (root, prefix)))
		# Run the distutils install_lib function.
		res = install_lib.run(self)
		# Change the datadir in useful.py back to '@datadir@'.
		replaceStr(filename, datadir, '@datadir@')
		return res

class dataInstall(install_data):
	## A class to extend the installation of data.
	def run(self):
		# Get the libdir.
		libDir = getattr(self.get_finalized_command('install'), 'install_lib')
		if (self.root and libDir.startswith(self.root)):
			# If root dir is defined, and the libDir starts with it, remove it
			# (and add 'whaawmp' to the end).
			basedir = os.path.join(libDir[len(self.root):], 'whaawmp')
			if not (basedir.startswith('/')): basedir = '/' + basedir
		else:
			# Otherwise, just add the 'whaawmp'.
			basedir = os.path.join(libDir, 'whaawmp')
		
		for x in scripts:
			# For all the scripts defined before.
			# Open the sh script file.
			f = open(x, 'w')
			# Write the appropriate command the the script then close it.
			f.write('#!/bin/sh\nexec %s %s/%s "$@"' % (sys.executable, basedir, scripts[x]))
			f.close()
			# Make it executable.
			os.system('chmod 755 %s' % x)
			# Run the distutils install_data function.
		return install_data.run(self)

# A list of tuples containing all the data files & their destinations.
data = [('share/whaawmp/ui', glob.glob('ui/*.ui')),
        ('share/whaawmp/images', (glob.glob('images/*.png') + glob.glob('images/*.svg'))),
        ('share/pixmaps', ['images/whaawmp.svg']),
        ('share/applications', ['whaawmp.desktop']),
        ('share/thumbnailers', ['whaaw-thumbnailer.desktop']),
        ('bin', scripts.keys())]

# The actual setup thing, mostly self explanatory.
setup(name="whaawmp", fullname="Whaaw! Media Player",
      version='0.2.14',
      description='Whaaw! Media Player',
      author='Jeff Bailes',
      author_email='thepizzaking@gmail.com',
      url='http://home.gna.org/whaawmp/',
      packages=['whaawmp','whaawmp.gui','whaawmp.common'],
      package_dir={'whaawmp': 'src'},
      data_files=data,
      cmdclass = {'install_lib' : libInstall,
                  'install_data' : dataInstall})
