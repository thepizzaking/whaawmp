#  Whaaw! Media Player gui init.
#  Copyright (C) 2007, Jeff Bailes <thepizzaking@gmail.com>
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

# Check that GTK+ is installed, and that an X server is available.
import sys, warnings

warnings.filterwarnings('error', module='gtk')
try:
	import gtk
except ImportError:
	print _("Cannot continue, pygtk is not installed (version 2.10 required)")
	sys.exit(1)
except Warning:
	print _("Cannot continue, X server not found!")
	sys.exit(1)
warnings.resetwarnings()

# Check that GTK+ 2.10 or greater is being used.
if (gtk.gtk_version < (2, 10) or gtk.pygtk_version < (2,10)):
	print _("Cannot continue, this program requires at least GTK+ 2.10 to run.")
	sys.exit(1)
