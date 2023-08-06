#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : Color selection widget connected to label widget (GTK3)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	16-Mar-2015
# .copyright  : (c) 2015 Fabrizio Pollastri.
# .license    : GNU General Public License (see below)
#
# This file is part of "AVC, Application View Controller".
#
# AVC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# AVC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# .-


import gi.repository.Gtk as Gtk		# gimp tool kit bindings

from avc import *		# AVC

UI_XML = 'gtk3_colorchooser.ui'	# GUI descriptor
ROOT_WINDOW = 'root_window'	# root window name


class Example(AVC):
  """
  Color selection widget connected to label widget (GTK3)
  """
  def __init__(self):

    # create GUI
    self.builder = Gtk.Builder()
    self.builder.add_from_file(UI_XML)
    self.builder.connect_signals(self)
    self.root_window = self.builder.get_object(ROOT_WINDOW)
    self.root_window.show_all()

    # all types of connected variables
    self.color_value = (0.25,0.50,1.,1.)


  def on_destroy(self,window):
    "Terminate program at window destroy"
    Gtk.main_quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
Gtk.main()  			 	# run GTK event loop until quit

#### END
