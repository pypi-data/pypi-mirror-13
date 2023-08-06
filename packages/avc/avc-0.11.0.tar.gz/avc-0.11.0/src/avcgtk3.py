# .+
# .context    : Application View Controller
# .title      : AVC GTK3 bindings
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	14-Mar-2015
# .copyright  :	(c) 2006-2015 Fabrizio Pollastri
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
# along with AVC.  If not, see <http://www.gnu.org/licenses/>.
#
# .-


#### IMPORT REQUIRED MODULES

import gi.repository.GObject as GObject	#---
import gi.repository.Gdk as Gdk 	#--
import gi.repository.Gtk as Gtk 	#- gimp tool kit bindings

import string			# string operations

#### GENERAL ABSTRACTION METHODS

def toplevel_widgets():
  "Return the list of all top level widgets"
  return Gtk.Window.list_toplevels()

def init(core):
  "Do init specific for this widget toolkit"
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = {
    Gtk.Button:			core['Button'],
    Gtk.Calendar:	    	core['Calendar'],
    Gtk.CheckButton:		core['ToggleButton'],
    Gtk.ComboBoxText:		core['ComboBox'],
    Gtk.ColorChooserWidget:	core['ColorChooser'],
    Gtk.Entry:    		core['Entry'],
    Gtk.Label:	    		core['Label'],
    Gtk.ProgressBar:		core['ProgressBar'],
    Gtk.RadioButton:  		core['RadioButton'],
    Gtk.HScale:			core['Slider'],
    Gtk.SpinButton:		core['SpinButton'],
    Gtk.Statusbar:    		core['StatusBar'],
    Gtk.TextView:		core['TextView'],
    Gtk.ToggleButton:		core['ToggleButton'],
    Gtk.TreeView:		core['listtreeview'],
    Gtk.VScale:			core['Slider']}
  # get toolkit version
  core['avccd'].toolkit_version = '{}.{}.{}'.format(
    Gtk.get_major_version(),Gtk.get_minor_version(),Gtk.get_micro_version())

def widget_children(widget):
  "Return the list of all children of the widget"
  # widgets that are not a subclass of gtk.Container have no children.
  if isinstance(widget,Gtk.Container):
    return widget.get_children()
  else:
    return []

def widget_name(widget):
  "Return the widget name"
  return widget.get_name()

def timer(function,period):
  """
  Start a GTK timer calling back 'function' every 'period' seconds.
  Return timer id.
  """
  return GObject.timeout_add(int(period * 1000.0),timer_wrap,function)

def timer_wrap(function):
  "Call given function and return True to keep timer alive"
  function()
  return True


class Error(Exception):
  "A generic error exception"
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)

class Widget:
  "GTK Widget Abstraction Layer abstract class"

  def __init__(self,allowed_types=None):
    # check for supported control type
    if allowed_types and not self.connection.control_type in allowed_types:
      raise Error('Control type "{}" not supported with "{}" widget.'.format(
        self.connection.control_type.__name__,self.widget.__class__.__name__))

  def connect_delete(self,widget,delete_method):
    "Connect widget delete method to destroy event"
    widget.connect("destroy",delete_method)


class ListTreeView(Widget):
  "Support to ListView and TreeView abstractors"

  def __init__(self):
    "Init operations common to ListView and TreeView"
    pass

  def append_column(self,col_num,text):
   "Append a column to the TreeView"
   self.widget.append_column(Gtk.TreeViewColumn(
     text,Gtk.CellRendererText(),text=col_num))


class Button(Widget):
  "GTK Button real widget abstractor"

  def __init__(self):
    # create button press status variable
    self.widget.value = False
    # connect relevant signals
    self.widget.connect("clicked",lambda event:
      self.connection.coget.__set__('',True,self.widget,self.connection))

  def read(self):
    "Get button status"
    status = self.widget.status
    self.widget.value = False
    return status

  def write(self,value):
    "Set button status"
    if value:
      self.widget.clicked()


class Calendar(Widget):
  "GTK Calendar real widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("day-selected",self.value_changed)

  def read(self):
    "Get calendar date"
    date = self.widget.get_date()
    # make month number starting from 1
    return (date[0],date[1]+1,date[2])

  def write(self,value):
    "Set calendar date"
    # make month number starting from 0
    self.widget.select_month(value[1]-1,value[0])
    self.widget.select_day(value[2])


class ColorChooser(Widget):
  "GTK ColorChooser real widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("color-activated",self.value_changed)

  def read(self):
    "Get current color"
    color = self.widget.get_rgba()
    return (color.red,color.green,color.blue,color.alpha)

  def write(self,value):
    "Set current color"
    self.widget.set_rgba(Gdk.RGBA(value[0],value[1],value[2],value[3]))


class ComboBox(Widget):
  "GTK ComboBox widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("changed",self.value_changed)

  def read(self):
    "Get index of selected item"
    return self.widget.get_active()

  def write(self,value):
    "Set selected item by its index value"
    self.widget.set_active(value)


class Entry(Widget):
  "GTK Entry widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("activate",self.value_changed)

  def read(self):
    "Get text from Entry"
    return self.widget.get_text()

  def write(self,value):
    "Set text into Entry"
    self.widget.set_text(str(value))


class Label(Widget):
  "GTK Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get value from Label"
    return self.widget.get_label()

  def write(self,value):
    "Set text into Label"
    self.widget.set_label(value)


class ListView(ListTreeView):
  "GTK TreeView widget abstractor"

  def __init__(self):
    # prepare data model.
    self.model = Gtk.ListStore(*self.row_types)
    # set model to widget
    self.widget.set_model(self.model)

    # connect relevant signals
    self.hid_row_deleted = self.model.connect("row-deleted",self.value_changed)
    self.hid_row_changed = self.model.connect("row-changed",self.value_changed)
    self.hid_rows_reordered = self.model.connect("rows-reordered",
      self.value_changed)


  def read(self):
    "Get values displayed by widget"
    # get head
    head = list(map(Gtk.TreeViewColumn.get_title,self.widget.get_columns()))
    # get data rows
    body = []
    #self.model.foreach(
    #  lambda model,path,iter,body: body.append(
    #    list(model.get(iter,*range(self.cols_num)))),body)
    for row in self.model:
      body.append(row[:])
    # return
    return {'head': head,'body': body}


  def write(self,value):
    "Set values displayed by widget"
    # prevent signal emission by program activity
    self.model.handler_block(self.hid_row_changed)
    self.model.handler_block(self.hid_row_deleted)
    # set header
    try:
      map(Gtk.TreeViewColumn.set_title,self.widget.get_columns(),value['head'])
    except:
      pass
    # set data rows
    body = value['body']
    self.model.clear()
    colsnum = self.model.get_n_columns()
    for row in body:
      model_iter = self.model.append(row)
      for col in range(colsnum):
        self.model.set_value(model_iter,col,row[col])
    # restore signal emission by user widget interaction
    self.model.handler_unblock(self.hid_row_changed)
    self.model.handler_unblock(self.hid_row_deleted)


class ProgressBar(Widget):
  "GTK ProgressBar widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get progress bar position"
    return self.widget.get_fraction()

  def write(self,value):
    "Set progress bar position"
    # negative values pulse the bar, positive values position the bar.
    if value < 0:
      self.widget.pulse()
    else:
      self.widget.set_fraction(value)


class RadioButton(Widget):
  "GTK RadioButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("clicked",self.value_changed)

  def read(self):
    "Get index of activated button"
    button = self.widget
    buttons = button.get_group()
    for index,rbutton in enumerate(buttons):
      if rbutton.get_active():
        break
    index = len(buttons) - index - 1
    return index

  def write(self,value):
    "Set activate button indexed by value"
    button = self.widget
    rbuttons = button.get_group()
    rbutton = rbuttons[len(rbuttons) - value - 1]
    rbutton.set_active(True)


class Slider(Widget):
  "GTK Slider widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("value-changed",self.value_changed)

  def read(self):
    "Get Slider value"
    return self.widget.get_value()

  def write(self,value):
    "Set Slider value"
    self.widget.set_value(value)


class SpinButton(Widget):
  "GTK SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("value-changed",self.value_changed)

  def read(self):
    "Get spinbutton value"
    return self.widget.get_value()

  def write(self,value):
    "Set spinbutton value"
    self.widget.set_value(value)


class StatusBar(Widget):
  "GTK StatusBar widget abstractor"

  def __init__(self):
    pass

  def write(self,value):
    "Set StatusBar value"
    self.widget.pop(1)
    self.widget.push(1,value)


class TextView(Widget):
  "GTK TextView widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.get_buffer().connect("changed",self.value_changed)

  def read(self):
    "Get text from TextView"
    textbuf = self.widget.get_buffer()
    return textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter(),
      False)

  def write(self,value):
    "Set text into TextView"
    self.widget.get_buffer().set_text(str(value))


class ToggleButton(Widget):
  "GTK ToggleButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("clicked",self.value_changed)

  def read(self):
    "Get button status"
    return self.widget.get_active()

  def write(self,value):
    "Set button status"
    self.widget.set_active(value)


class TreeView(ListTreeView):
  "GTK TreeView widget abstractor"

  def __init__(self):
    # prepare data model.
    self.model = Gtk.TreeStore(*self.row_types)
    # set model to widget
    self.widget.set_model(self.model)

    # connect relevant signals
    self.model.connect("row-deleted",self.value_changed)
    self.model.connect("row-changed",self.value_changed)


  def read(self):
    "Get values displayed by widget"
    # get head
    head = list(map(Gtk.TreeViewColumn.get_title,self.widget.get_columns()))
    # get data rows
    body = {}
    # recursive depth first tree data node reader
    def read_node(node_iter,parent_id):
      node_id = '.'.join(
        list(map(lambda x: str(x+1),self.model.get_path(node_iter))))
      body[node_id] = list(self.model.get(node_iter,*range(self.cols_num)))
      child_iter = self.model.iter_children(node_iter)
      while child_iter:
        read_node(child_iter,node_id)
        child_iter = self.model.iter_next(child_iter)
    node_iter = self.model.get_iter_first()
    while node_iter:
      read_node(node_iter,None)
      node_iter = self.model.iter_next(node_iter)
    # return
    return {'head': head,'body': body}

  def write_head(self,head):
    "Write header"
    map(Gtk.TreeViewColumn.set_title,self.widget.get_columns(),head)

  def root_node(self):
    "Return the root node of the tree"
    return None

  def add_node(self,parent,last_node,current_depth,data):
    "Add current node to the tree"
    return self.model.append(parent,data)


#### END
