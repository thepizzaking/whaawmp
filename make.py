#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install import install as _install
from distutils.command.install_data import install_data
from distutils import cmd
import glob
import os

scripts = {'whaawmp' : 'whaawmp.py',
           'whaaw-thumbnailer' : 'thumbnailer.py'}

class fixDataPath(cmd.Command):
	def initialize_options(self):
		self.prefix = None
		self.lib_build_dir = None
		self.libdir = None

	def finalize_options(self):
		self.set_undefined_options('install', ('prefix', 'prefix'))
		self.set_undefined_options('install', ('libdir', 'libdir'))
		self.set_undefined_options('build', ('build_lib', 'lib_build_dir'))

	def run(self):
		print self.libdir
		filename = os.path.join(self.lib_build_dir, 'whaawmp', 'common', 'useful.py')
		file = open(filename, 'r')
		data = file.read()
		file.close()
		data = data.replace('@datadir@', os.path.join(self.prefix, 'share', 'whaawmp'))
		file = open(filename, 'w')
		file.write(data)
		file.close()

	def get_outputs(self): return []

class install(_install):
	sub_commands = [('fixDataPath', None)] + _install.sub_commands
	def run(self):
		_install.run(self)

class smartInstall(install_data):
	def run(self):
		install_cmd = self.get_finalized_command('install')
		libDir = getattr(install_cmd, 'install_lib')
		basedir = os.path.join(libDir[len(self.root):], 'whaawmp')
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
      cmdclass = {'fixDataPath': fixDataPath,
                  'install_data': smartInstall})
