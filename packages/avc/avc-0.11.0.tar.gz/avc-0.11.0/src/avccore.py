# -*- coding: utf-8 -*-
# .+
# .context    : Application View Controller
# .title      : AVC core
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	3-Nov-2006
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


# import required modules
import copy				# object deep copy
import sys				# command line option reading


class Error(Exception):
    """A generic error exception"""

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


## module information
__author__ = 'Fabrizio Pollastri <f.pollastri@inrim.it>'
__license__ = '>= GPL v3'
__version__ = '0.11.0'


## load proper AVC widget toolkit binding according with the widget toolkit
# imported by application program

# supported toolkit names indexed by python binding module names
TOOLKITS = {
  'gtk':'GTK+',
  'gi.repository.Gtk':'GTK3',
  'PyQt4':'Qt4',
  'javax':'Swing',
  'Tkinter':'Tkinter',
  'tkinter':'tkinter',
  'wx':'wxWidgets'}

# avc toolkit bindings indexed by python binding module names
AVC_BINDINGS = {
  'gtk':'avcgtk',
  'gi.repository.Gtk':'avcgtk3',
  'PyQt4':'avcqt4',
  'javax':'avcswing',
  'Tkinter':'avctk',
  'tkinter':'avctk',
  'wx':'avcwx'}

AVC_PREFIX = 'avc.'

# test which widget toolkit binding module is imported: if none raise an error.
for toolkit in TOOLKITS.keys():
  if toolkit in sys.modules:
    break
else:
  raise Error('No supported toolkit found: import it before AVC import.')

# found a supported toolkit: import its AVC binding
real = __import__(AVC_PREFIX + AVC_BINDINGS[toolkit],globals(),locals(),
  [AVC_BINDINGS[toolkit]])


# command line option switches
OPT_VERBOSITY = '--avc-verbosity'

# separator between widget name part 1 and 2
WIDGET_NAME_SEP = '__'

# AVC common data
class AVCcd:
  def __init__(self):
    self.toolkit_version = ''
    self.verbosity = 0
    self.view_period = 0.1
    self.widget_map = {}
    self.cogets = {}
    self.connections = {}
    self.connections_updates = {}
    self.connected_widgets = {}
    self.timer = None
    self.avc = None
avccd = AVCcd()


class AVC(object):
  "AVC programming interface"

  def avc_init(self,verbosity=0,view_period=0.1):
    "Init AVC core logic"

    # save parameters as globals
    avccd.verbosity = verbosity
    avccd.view_period = view_period

    # save itself
    avccd.avc = self

    # if any, get options from command line and override init arguments
    try:
      opt_switch_index = sys.argv.index(OPT_VERBOSITY)
      avccd.verbosity = int(sys.argv[opt_switch_index+1])
    except:
      pass

    # do init specific to widget toolkit
    real.init(globals())

    # if verbosity > 0 , print header
    if avccd.verbosity > 0:
      self.print_header()

    # connect widgets-variables in __main__ namespace
    self.avc_connect(real.toplevel_widgets())

    # if a sampled (periodic) update of all controls views is required,
    # start a periodic call to view update function.
    if avccd.view_period != 0.0:
      avccd.timer = real.timer(self.view_update,avccd.view_period)


  def avc_connect(self,toplevel):
    """
    For each widget at or below toplevel, having a matching name with
    an attribute of object_ object, create a widget-attribute connection.
    """

    # check for avc_init execution
    if not avccd.widget_map:
      raise Error("avc_connect must be called after avc_init call.")

    # force top level widgets to be a list
    if toplevel.__class__ != list:
      toplevel = [toplevel]

    if avccd.verbosity > 3:
      print('widget tree scansion from top level {}'.format(toplevel))

    # for each widget in GUI ...
    for widget, widget_name in self.get_widget(toplevel):

      # if widget is not supported: go to next widget
      if widget.__class__ not in avccd.widget_map:

        if avccd.verbosity > 3:
          print('  skip unsupported widget {},"{}"'.format(
            widget.__class__.__name__,widget_name))

        continue

      # if the widget is already connected: go to next widget.
      if widget in avccd.connected_widgets:

        if avccd.verbosity > 3:
          print('  skip already connected widget {},"{}"'.format(
            widget.__class__.__name__,widget_name))

        continue

      # control name is the widget name part before WIDGET_NAME_SEP string,
      # if present, otherwise is the whole widget name.
      control_name = widget_name.split(WIDGET_NAME_SEP)[0]

      # if no object attribute with the same name: go to next widget.
      if not hasattr(self,control_name):

        if avccd.verbosity > 3:
          print('  skip unmatched widget {},"{}"'.format(
            widget.__class__.__name__,widget_name))

        continue

      ## there exists an application attribute with the same name

      # if the connection exists, get it from connections dictionary,
      # if the connection does not exists, create it.
      connection = avccd.connections.setdefault(
        (control_name,self),
        Connection(getattr(self,control_name)))

      # add widget to connection and mark widget as connected
      connection.add_widget(control_name,self,widget,widget_name)
      avccd.connected_widgets[widget] = connection


  def get_widget(self,widgets):
    """
    Widget tree iterator. Start from toplevel widgets and traverse their
    widgets trees in breath first mode returning for each widget its
    pointer and name.
    """
    # for each toplevel widget ...
    while widgets:
      children = []
      # for each widget in this level ...
      for widget in widgets:
        # return pointer and name of widget
        yield (widget,real.widget_name(widget))
        children += real.widget_children(widget)
      # children of this level are widgets of next level
      widgets = children


  def view_update(self):
    "Periodically update views for all scheduled cogets"

    for connection in avccd.connections_updates.keys():
      setter = avccd.connections_updates[connection]
      # set the new control value in all widgets binded to this control
      # excluding the setting widget, if setter is a widget.
      for wal_widget in connection.wal_widgets:
        if wal_widget != setter:
          try:
            wal_widget.write(connection.control_value)
          # on writing error terminate
          except:
            print('error writing {} to {}:'.format(
              connection.control_value,wal_widget))
            print(sys.exc_info()[1])
            sys.exit()

    # clear all update requests
    avccd.connections_updates = {}


  def dump(self):
    "Printout all internal data"

    print('++++ AVC internal data dump ++++')

    # cogets
    print('cogets')
    print('\n'.join([coget.__str__('  ')
      for key, coget in avccd.cogets.items()]))

    # connections to be updated
    print('connections to be updated')
    print('\n'.join(['{}\n    setter: {}'.format(conn.__str__('  '),setter)
      for conn, setter in avccd.connections_updates.items()]))

    # timer
    print('timer {}'.format(avccd.timer))

    print('---- AVC internal data dump end ----')


  def print_header(self):
    "Printout header data"

    print('AVC {} - Activity Report'.format(__version__))
    print('python version: {}'.format(sys.version.replace('\n','')))
    print('widget toolkit binding: {} v{}'.format(
      TOOLKITS[toolkit],avccd.toolkit_version))
    print('program: {}'.format(sys.argv[0]))
    print('verbosity: {}'.format(avccd.verbosity))
    if avccd.view_period:
      print('connection update mode: periodic, period={} sec'.format(
        avccd.view_period))
    else:
      print('connection update mode: immediate')


class Connection:
  "Widgets-variable connection"

  def __init__(self,control_value=None):

    # set storage for control value, type, connected wal widget list,
    # value changed handler and coget
    self.control_value = control_value
    self.control_type = control_value.__class__
    self.wal_widgets = []
    self.set_handler = None
    self.object_ = None
    self.coget = None


  def add_widget(self,control_name,object_,widget,widget_name):
    "Add one widget to current connection"

    ## if it is the first widget, setup connection control data and coget

    if not self.wal_widgets:

      # save connection object instance
      self.object_ = object_

      # if exists a object method with the name control_name+'_changed',
      # store it, it will be called when a widget set a new control value.
      try:
        self.set_handler = getattr(object_,'{}_changed'.format(control_name))
      except AttributeError:
        pass

      # if the corresponding coget does not exists, create it, if exists,
      # get it from cogets dictionary.
      try:
        self.coget = avccd.cogets[(control_name,object_.__class__)]
      except KeyError:
        coget = Coget(control_name,object_)
        avccd.cogets[(control_name,object_.__class__)] = coget
        self.coget = coget
        # set coget as an property in place of application variable.
        setattr(object_.__class__,control_name,coget)

      # save connection reference into coget
      self.coget.add_connection(self)

      if avccd.verbosity > 0:
        print('  creating connection "{}" in {}'.format(control_name,object_))
        print('    type: {}'.format(self.control_type))
        print('    initial value: {}'.format(self.control_value))
        if self.set_handler:
          print('    connected handler "{}_changed"'.format(control_name))

    # map the connected widget into the corresponding abstract widget
    wal_widget = avccd.widget_map[widget.__class__]

    if avccd.verbosity > 1:
      print('  add widget {},"{}" to connection "{}"'.format(
        widget.__class__.__name__,widget_name,control_name))

    # add it to the wal widget list
    self.wal_widgets.append(wal_widget(self,widget))

    # init it with the control value
    self.wal_widgets[-1].write(self.control_value)


  def remove_widget(self,wal_widget):
    """
    Remove one widget from current connection. If it is the last
    one in the connection, delete the connection.
    """

    if avccd.verbosity > 4:
      avccd.avc.dump()

    self.wal_widgets.remove(wal_widget)

    if avccd.verbosity > 1:
      print('removing widget {} from connection "{}" of {}'.format(
        wal_widget.widget.__class__.__name__,
        self.coget.control_name,
        self.object_))

    # clear wal widget data
    del wal_widget.connection
    del wal_widget.widget


    # if connection has no more widgets delete it
    if not self.wal_widgets:

      if avccd.verbosity > 0:
        print('removing connection "{}" from {}'.format(
          self.coget.control_name,self.object_))

      # delete connection from those with a pending update
      try:
        del avccd.connections_updates[self]
      except KeyError:
        pass

      # restore application variable to its bare value (remove coget from it)
      #setattr(self.object_,self.coget.control_name,self.control_value)

      # delete connection from general connection dictionary
      del avccd.connections[(self.coget.control_name,self.object_)]

      # delete connection from coget
      self.coget.remove_connection(self)

      # clear connection data
      del self.control_value
      del self.control_type
      del self.wal_widgets
      del self.set_handler
      del self.object_
      del self.coget


  def __str__(self,indent='',name=None,object_=None):
    "Human readable representation of connection"
    conn = ['{}connection: {}'.format(indent,object.__str__(self))]
    if name:
      conn.append('{}  name:          {}'.format(indent,name))
    if object_:
      conn.append('{}  object:        {}'.format(indent,object_))
    conn.append('{}  control value: {}'.format(indent,self.control_value))
    conn.append('{}  control type:  {}'.format(indent,self.control_type))
    conn.append(
      '{}  coget:         {}'.format(indent,object.__str__(self.coget)))
    conn.append('{}  set handler:   {}'.format(indent,self.set_handler))
    conn.append('{}  wal widgets'.format(indent))
    for wal_widget in self.wal_widgets:
      conn.append(wal_widget.__str__('{}    '.format(indent)))
    return '\n'.join(conn)


class Coget(object):
  "A control object as data descriptor"

  def __init__(self,control_name,object_):
    "Create the coget control and bind it to one attribute in object"

    if avccd.verbosity > 3:
      print('  creating coget "{}" in {}'.format(
        control_name,object.__str__(self)))

    # save argument
    self.control_name = control_name
    self.connections = []


  def add_connection(self,connection):
    "Add a connection"
    self.connections.append(connection)

  def remove_connection(self,connection):
    "Remove a connection. If it is the last one, delete coget."
    self.connections.remove(connection)
    if not self.connections:

      if avccd.verbosity > 3:
        print('deleting coget "{}" {}'.format(
          self.control_name,object.__str__(self)))

      # restore property to its bare value (remove coget from it)
      #setattr(connection.object_.__class__,self.control_name,
      #  connection.control_value)

      del avccd.cogets[(self.control_name,connection.object_.__class__)]
      del self.connections
      del self.control_name


  def __get__(self,object_,classinfo):
    "Get control value"
    return avccd.connections[(self.control_name,object_)].control_value


  def __set__(self,object_,value,setter=None,connection=None):
    """
    Set a new control value into application control variable. If setter
    is a widget (setter != None), call the application set handler, if exists.
    Update control view in all widgets binded to the control, if setter is
    a widget, do not update it.
    """
    # if not given, get or create connection
    if not connection:
      # if the connection exists, get it from connections dictionary,
      # otherwise, create it.
      try:
        connection = avccd.connections[(self.control_name,object_)]
      except KeyError:
        connection = Connection(value)
        avccd.connections[(self.control_name,object_)] = connection
        return

    # if control old value equal to the new one, return immediately.
    if value == connection.control_value:
      return

    # set new control value: if control is a mutable sequence (list) or
    # mapping (dict), a full copy inside the coget is needed to test if it
    # is really changed.
    if connection.control_type in (list,dict):
      try:
        connection.control_value = copy.deepcopy(value)
      except:
        try:
          #del value['head']
          a = copy.deepcopy(value)
        except:
          print('*********************************')
          print(value)
    else:
      connection.control_value = value

    # if setter is a widget, call the application set handler for this
    # control, if exists.
    if setter and connection.set_handler:
      connection.set_handler(value)

    # if a sampled view update is required, schedule this coget for
    # view update.
    if avccd.view_period != 0.0:
      avccd.connections_updates[connection] = setter
      return

    # if an immediate update is required, set the new control value
    # in all widgets binded to this control excluding the setting
    # widget, if setter is a widget.
    for wal_widget in connection.wal_widgets:
      if wal_widget != setter:
        wal_widget.write(value)


  def __delete__(self,instance):
    "Cogets cannot be deleted"
    raise Error('Trying to delete {}: Cogets cannot be deleted.'.format(self))


  def __str__(self,indent=''):
    "Human readable representation of coget"
    coget = ['{}coget: {}'.format(indent,object.__str__(self))]
    coget.append('{}  name:          {}'.format(indent,self.control_name))
    coget.append('{}  connections'.format(indent))
    for connection in self.connections:
      coget.append(connection.__str__(indent + '    '))
    return '\n'.join(coget)


#### WIDGETS ABSTRACTION LAYER (coget side)

class Widget:
  "Widget Abstraction Layer abstract class"

  def __init__(self,connection,widget,allowed_types=None):

    # check for supported control type
    if allowed_types and not connection.control_type in allowed_types:
      raise Error('Control type "{}" not supported with "{}" widget.'.format(
        connection.control_type.__name__,widget.__class__.__name__))

    # save references
    self.connection = connection
    self.widget = widget

    # connect signal common to all widgets
    self.connect_delete(widget,self.delete)


  def read(self):
    raise Error('Method "read" of abstract class Widget is undefined.')

  def write(self,value):
    raise Error('Method "write" of abstract class Widget is undefined.')

  def value_changed(self,*args):
    "widget value changed handler"
    # set new value into control variable
    Coget.__set__(
      self.connection.coget,'',self.read(),self,self.connection)

  def delete(self,*args):
    "delete widget from connection"
    self.connection.remove_widget(self)

  def __str__(self,indent=''):
    "human readable representation"
    walwidget = ['{}wal widget: {}'.format(indent,object.__str__(self))]
    walwidget.append('{}  real widget: {}'.format(indent,self.widget))
    walwidget.append('{}  connection:  {}'.format(indent,object.__str__(self.connection)))
    return '\n'.join(walwidget)


class ListTreeView(Widget,real.ListTreeView):

  def __init__(self,connection,listtreeview):
    "Common init operations for ListView and TreeView abstractors"

    # generic abstract widget init
    Widget.__init__(self,connection,listtreeview,(dict,))

    # check for allowed control type
    head = connection.control_value.get('head',None)
    if head and type(head) != list:
      raise Error(
        '{} widget do not allow "{}" type as header, use a list.'.format(
          listtreeview.__class__.__name__,type(head).__name__))

    # save column number
    self.cols_num = len(self.row_types)

    # check for header size equal to column number
    if head and len(head) != self.cols_num:
      raise Error(
        '{} widget require header length equal to data row size.'.format(
          listtreeview.__class__.__name__))

    # real common init
    real.ListTreeView.__init__(self)

    # add required columns to TreeView widget with title (header), if required.
    head = self.connection.control_value.get('head',None)
    if head:
      for col, col_head in enumerate(head):
        self.append_column(col, col_head)
    else:
      for col in range(self.cols_num):
          self.append_column(col, '')


class Button(real.Button,Widget):
  "Button widget abstractor"

  def __init__(self,connection,button):
    # generic abstract widget init
    Widget.__init__(self,connection,button,(bool,))
    # real widget init
    real.Button.__init__(self)


class Calendar(real.Calendar,Widget):
  "Calendar widget abstractor"

  def __init__(self,connection,calendar):
    # generic abstract widget init
    Widget.__init__(self,connection,calendar,(list,tuple))
    # real widget init
    real.Calendar.__init__(self)


class ComboBox(real.ComboBox,Widget):
  "ComboBox widget abstractor"

  def __init__(self,connection,combobox):
    # generic abstract widget init
    Widget.__init__(self,connection,combobox,(int,))
    # real widget init
    real.ComboBox.__init__(self)


class ColorChooser(real.ColorChooser,Widget):
  "ColorChooser widget abstractor"

  def __init__(self,connection,colorchooser):
    # generic abstract widget init
    Widget.__init__(self,connection,colorchooser,(list,tuple))
    # real widget init
    real.ColorChooser.__init__(self)


class Entry(real.Entry,Widget):
  "Entry widget abstractor"

  def __init__(self,connection,entry):
    # generic abstract widget init
    Widget.__init__(self,connection,entry,(float,int,str))
    # real widget init
    real.Entry.__init__(self)

  def read(self):
    "Get Entry value"
    return self.connection.control_type(real.Entry.read(self))


class Label(real.Label,Widget):
  "Label widget abstractor"

  def __init__(self,connection,label):

    # generic abstract widget init
    Widget.__init__(self,connection,label)

    # check for generic python object
    if connection.control_type in (bool,float,int,list,str,tuple,dict):
      self.is_object = False
      control_value = connection.control_value
    else:
      self.is_object = True
      control_value = connection.control_value.__dict__

    # get default format string, if any.
    self.format = str(self.read())

    # check for a working format
    try:
      # new type format strings
      if connection.control_type == list:
        junk = self.format.format(*control_value)
        if junk == self.format:
          raise
      elif connection.control_type == dict:
        junk = self.format.format(**control_value)
        if junk == self.format:
          raise
      else:
        junk = self.format.format(control_value)
        if junk == self.format:
          raise
      if avccd.verbosity > 2:
        print('    valid new format string: "{}"'.format(self.format))
    except:
      try:
        # old type format with '%s' etc.
        if connection.control_type == list:
          junk = self.format % tuple(control_value)
        elif connection.control_type == dict:
          junk = self.format % control_value
          if junk == self.format:
            raise
        else:
          junk = self.format % control_value
        if avccd.verbosity > 2:
          print('    valid old format string: "{}"'.format(self.format))
      except:
        if avccd.verbosity > 2:
          if self.format:
            print('    invalid format string: "{}"'.format(self.format))
          else:
            print('    no format string')
        self.format = None

    # real widget init
    real.Label.__init__(self)


  def read(self):
    "Get value from Label"
    # if control type is a generic object do not coerce to its type
    if self.is_object:
      return real.Label.read(self)
    # if control type not a generic object,first try to coerce to control type
    try:
      return self.connection.control_type(eval(real.Label.read(self)))
    # if fail, return value as string, needed for format string initial get.
    except:
      return real.Label.read(self)

  def write(self,value):
    "Set text into Label"
    if self.format:
      if self.is_object:
        try:
          # New type format string
          label = self.format.format(**value.__dict__)
          if label == self.format:
            raise
          real.Label.write(self, label)
        except:
          # Old type format with '%s'
          real.Label.write(self, self.format % value.__dict__)
      elif type(value) == list:
        try:
          # New type format string
          label = self.format.format(*value)
          if label == self.format:
            raise
          real.Lable.write(self, label)
        except:
          # Old type format with '%s'
          real.Label.write(self, self.format % tuple(value))
      else:
        try:
          # New type format string
          label = self.format.format(value)
          if label == self.format:
            raise
          real.Lable.write(self, label)
        except:
          # Old type format with '%s'
          real.Label.write(self,self.format % value)
    else:
      real.Label.write(self,str(value))


class ListView(real.ListView,ListTreeView):
  "ListView widget abstractor"

  def __init__(self,connection,listview):

    # save data row types
    body = connection.control_value.get('body',None)
    if type(body[0]) == list:
      self.row_types = [type(item) for item in body[0]]
    else:
      self.row_types = [type(body[0])]

    # common init
    ListTreeView.__init__(self,connection,listview)

    # real widget init
    real.ListView.__init__(self)


class ProgressBar(real.ProgressBar,Widget):
  "ProgressBar widget abstractor"

  def __init__(self,connection,progressbar):
    # generic abstract widget init
    Widget.__init__(self,connection,progressbar,(float,int))
    # real widget init
    real.ProgressBar.__init__(self)

  def read(self):
    "Get Entry value"
    return self.connection.control_type(real.Entry.read(self))


class RadioButton(real.RadioButton,Widget):
  "RadioButton widget abstractor"

  def __init__(self,connection,radiobutton):
    # generic abstract widget init
    Widget.__init__(self,connection,radiobutton,(int,))
    # real widget init
    real.RadioButton.__init__(self)


class Slider(real.Slider,Widget):
  "Slider widget abstractor"

  def __init__(self,connection,slider):
    # generic abstract widget init
    Widget.__init__(self,connection,slider,(float,int))
    # real widget init
    real.Slider.__init__(self)

  def read(self):
    "Get Slider value"
    return self.connection.control_type(real.Slider.read(self))


class SpinButton(real.SpinButton,Widget):
  "SpinButton widget abstractor"

  def __init__(self,connection,spinbutton):
    # generic abstract widget init
    Widget.__init__(self,connection,spinbutton,(float,int))
    # real widget init
    real.SpinButton.__init__(self)

  def read(self):
    "Get spinbutton value"
    return self.connection.control_type(real.SpinButton.read(self))


class StatusBar(real.StatusBar,Widget):
  "StatusBar widget abstractor"

  def __init__(self,connection,statusbar):
    # generic abstract widget init
    Widget.__init__(self,connection,statusbar,(str,))
    # real widget init
    real.StatusBar.__init__(self)


class TextView(real.TextView,Widget):
  "TextView widget abstractor"

  def __init__(self,connection,textview):
    # generic abstract widget init
    Widget.__init__(self,connection,textview,(str,))
    # real widget init
    real.TextView.__init__(self)


class ToggleButton(real.ToggleButton,Widget):
  "ToggleButton widget abstractor"

  def __init__(self,connection,togglebutton):
    # generic abstract widget init
    Widget.__init__(self,connection,togglebutton,(bool,))
    # real widget init
    real.ToggleButton.__init__(self)


class TreeView(real.TreeView,ListTreeView):
  "TreeView widget abstractor"

  def __init__(self,connection,treeview):

    # save data row types
    body = connection.control_value.get('body',None)
    for row in body.values():
        self.row_types = [type(row_item) for row_item in row]
        break

    # common init
    ListTreeView.__init__(self,connection,treeview)

    # real widget init
    real.TreeView.__init__(self)


  def write(self,value):
    "Set values displayed by widget"
    # set header
    try:
      self.write_head(value['head'])
    except KeyError:
      pass
    # set data rows
    body = value['body']
    # sort node ids in depth first order
    node_ids = body.keys()
    nodes = [([int(i) for i in id.split('.')], id) for id in node_ids]
    # depth first tree data node writer
    current_depth = 1
    parents = [self.root_node()]
    last_node = None
    for node in sorted(nodes):
      node_depth = len(node[0])
      if node_depth > current_depth:
        parents.append(last_node)
        current_depth = node_depth
      elif node_depth < current_depth:
        last_node = parents.pop(-1)
        current_depth = node_depth
      last_node = self.add_node(parents[-1],last_node,current_depth,
        body[node[1]])


## support functions

# support for ListView and TreeView abstractors"

def listtreeview(connection,treeview):
  """
  Route real tree view widgets supporting both list and tree data structures
  to the abstract widgets supporting only list or tree data.
  """
  body = connection.control_value.get('body',None)
  body_type = type(body)
  if body_type == list:
    return ListView(connection,treeview)
  elif body_type == dict:
    return TreeView(connection,treeview)
  else:
    raise Error(
      '{} widget do not allow "{}" type as data, '
      'use a list for tabular data or a dictionary for tree data.'.format(
        treeview.__class__.__name__,type(body).__name__))


#### END
