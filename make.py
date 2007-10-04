#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install_lib import install_lib
import distutils.dir_util
from distutils import cmd
import glob
import os

scripts = {'whaawmp' : 'whaawmp.py',
           'whaaw-thumbnailer' : 'thumbnailer.py'}

class libInstall(install_lib):
	def run(self):
		root = getattr(self.get_finalized_command('install'), 'root')
		prefix = getattr(self.get_finalized_command('install'), 'prefix')
		libDir = getattr(self.get_finalized_command('build'), 'build_lib')
		# To fix the datadir location.
		filename = os.path.join(libDir, 'whaawmp', 'common', 'useful.py')
		f = open(filename, 'r')
		data = f.read()
		f.close()
		data = data.replace('@datadir@', os.path.join(prefix, 'share', 'whaawmp'))
		f = open(filename, 'w')
		f.write(data)
		f.close()
		# Install the locales.
		os.system('./po/potool.py compile')
		distutils.dir_util.copy_tree('po/locale', ('%s%s/share/locale' % (root, prefix)))
		return install_lib.run(self)

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
