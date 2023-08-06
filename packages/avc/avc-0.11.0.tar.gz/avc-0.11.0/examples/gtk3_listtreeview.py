#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : tree view widget display capabilities (GTK3)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	20-Mar-2015
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


import gi.repository.GObject as GObject	#--
import gi.repository.Gtk as Gtk		#- gimp tool kit bindings

from avc import *			# AVC

import copy				# object cloning support

UI_XML = 'gtk3_listtreeview.ui'         # GUI descriptor
ROOT_WINDOW = 'root_window'		# root window name
UPDATE_PERIOD = 2000			# ms


class Example(AVC):
  """
  Showcase of display capabilities for the tree view widget
  """

  def __init__(self):

    # create GUI
    self.builder = Gtk.Builder()
    self.builder.add_from_file(UI_XML)
    self.builder.connect_signals(self)
    self.root_window = self.builder.get_object(ROOT_WINDOW)
    self.root_window.show_all()

    # make tree view rows reorderable
    self.builder.get_object('list__treeview').set_reorderable(True)
    self.builder.get_object('tree__treeview').set_reorderable(True)

    # connected variables
    self.list = {'head':['col1 int','col2 str'], \
      'body':[[1,'one'],[2,'two'],[3,'three']]}
    self.list_work = copy.deepcopy(self.list)
    self.tree = {'head':['col1 int','col2 str'],'body':{ \
      # root rows
      '1':[1,'one'], \
      '2':[2,'two'], \
      # children of root row '1'
      '1.1':[11,'one one'], \
      '1.2':[12,'one two'], \
      # children of root row '2'
      '2.1':[21,'two one'], \
      '2.2':[22,'two two']}}

    # start variables update
    update = self.update()
    try: # python 2 and 3 compatibility
      self.timer = GObject.timeout_add(UPDATE_PERIOD,update.next)
    except:
      self.timer = GObject.timeout_add(UPDATE_PERIOD,update.__next__)
      

  def update(self):
    """
    Tabular data rows data are rolled down.
    """
    rows_num = len(self.list['body'])
    while True:
      # save last row of data
      last_row = self.list_work['body'][-1]
      # shift down one position each data row
      for i in range(1,rows_num): 
        self.list_work['body'][-i] = \
          self.list_work['body'][-1-i]
      # copy last row into first position
      self.list_work['body'][0] = last_row
      # copy working copy into connected variable
      self.list = self.list_work
      yield True


  def on_destroy(self,window):
    "Terminate program at window destroy"
    Gtk.main_quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
Gtk.main()			 	# run GTK event loop until quit

#### END
