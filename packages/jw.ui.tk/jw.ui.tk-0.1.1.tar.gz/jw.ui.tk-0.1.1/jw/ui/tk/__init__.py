# Copyright 2016 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Tk GUI
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import logging
from tkinter.tix import Tk, ScrolledWindow
from tkinter import Listbox, BOTH, VERTICAL, HORIZONTAL, END
from tkinter.ttk import Treeview, PanedWindow, Labelframe, Frame, Scrollbar, Notebook as TkNotebook
import time

from functools import partial
from collections import namedtuple
from gevent import sleep
from memoizer import memoize
from pkg_resources import iter_entry_points
from zope.interface.registry import Components
from jw.ui import base

from builtins import object
from zope import component
from zope.interface import implementer

_Logger = logging.getLogger(__name__)
_Components = Components(__name__)

UNSPECIFIED_TOPIC = 'unspecified'
STANDARD_PADDING = 3

class Scrolled(Frame):
    """
    Scrolled widget
    """

    Config = namedtuple('Config', ('orient', 'command', 'column', 'row', 'sticky', 'scrollcommand'))

    CONFIG = {
        'x': Config('horizontal', 'xscrollcommand', 0, 1, 'nswe', 'xview'),
        'y': Config('vertical', 'yscrollcommand', 1, 0, 'nswe', 'yview')
    }

    def __init__(self, parent, widgetClass, dimensions='xy', *args, **kwargs):
        """
        Create scrolled widget

        :param parent: parent widget
        :param widgetClass: widget class
        :param dimensions: 'x' or 'y'
        :param args: args for instatiating widget
        :param kwargs: kwargs for instantiating widget
        """
        Frame.__init__(self, parent)
        self.dimensions = dimensions
        self.scrollbar = {}
        self.widget = widgetClass(self, *args, **kwargs)
        self.widget.grid(row=0, column=0, sticky='nswe')
        for d in dimensions:
            self.addScrollbar(d)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def addScrollbar(self, dimension):
        """
        Add scrollbar

        :param dimension: 'x' or 'y'
        :type dimension: str
        """
        assert dimension in 'xy'
        config = self.CONFIG[dimension]
        s = self.scrollbar[dimension] = Scrollbar(
            self, orient=config.orient, command=getattr(self.widget, config.scrollcommand)
        )
        s.grid(row=config.row, column=config.column, sticky=config.sticky)
        self.widget[config.command] = s.set

@implementer(base.Ui)
class Ui(object):
    """
    Tk GUI object
    """

    def __init__(self):
        """
        Create Ui object

        """
        self.running = False
        self.mainRegistry = set()

    def setup(self, **kwargs):
        """
        Setup user interface

        :param kwargs:
        :type kwargs:
        """

    @memoize
    def widgetClass(self, name):
        """
        Get widget class from name

        :param name: widget class symbolic name
        :type name: str
        """
        wclass = next(iter_entry_points('jw.eventview.widget', name), None)
        if wclass:
            return wclass.load()
        raise RuntimeError('Control class not found: %s' % name)

    def run(self, stopCallback):
        """
        Run user interface

        """
        self.running = True
        while self.running:
            self.update()
            sleep(.05)  # TODO: adapt dynamically
        print('UI stopped')
        stopCallback()

    def stop(self):
        print('Stopping UI')
        self.running = False

    def update(self):
        """
        Update windows
        """
        for w in self.mainRegistry:
            w.update()

    def minimizeAll(self):
        """
        Minimize all windows
        """
        for window in self.mainRegistry:
            window.iconify()
            #window.withdraw()

    def restoreAll(self):
        """
        Restore all minimzed windows
        """
        for window in self.mainRegistry:
            window.deiconify()

    def register(self, window):
        """
        Register a main window
        """
        self.mainRegistry.add(window)

_Tk = Ui()
component.provideUtility(_Tk, base.Ui, 'tk')

@implementer(base.DisplayControl)
class Control(object):
    """
    Tk widget
    """

    def __init__(self, parent, **kwargs):
        """
        Create a Control object

        Must be called by derived classes before placing widgets
        """
        self.parent = parent
        self.kwargs = kwargs

    def report(self, message, show=False):
        """
        Report event

        :param message: event
        :type message: dict
        :param show: whether to switch to element reported
        :type show: bool

        Expected to fill message data into user interface
        """
        raise NotImplementedError()

    def collectStatus(self):
        """
        Update control status

        Expected to put all status information in the dict provided by self.kwargs['status'] if non-null
        """
        #raise NotImplementedError()

    def messageTopic(self, message, default=''):
        """
        Get title

        :return: topic field handled by this widget
        :rtype: str

        Returns either the message's topic according to this widget's definition of a default
        """
        topic_ = self.kwargs.get('topic')
        if topic_:
            return message.get(topic_, UNSPECIFIED_TOPIC.format(topic=topic_))
        else:
            return default

@memoize
def PluginClass(extensionNamespace, name, type_=type):
    """
    Load plugin class

    :param extensionNamespace: extension namespace
    :type extensionNamespace: str
    :param name: class name
    :type name: str
    :param type_: expected type
    :type type_: type
    :return: class
    :rtype: type

    Searches an extension for a name and loads this as a class
    """
    try:
        ep = next(iter_entry_points(extensionNamespace, name))
    except StopIteration:
        raise RuntimeError('No class "%s" in extension namespace "%s"' % (name, extensionNamespace))
    result = ep.load()
    assert isinstance(result, type_)
    return result

class DetailControl(Control):
    """
    Class of controls switching their content according to the selection of a master control
    """

    def __init__(self, parent, **kwargs):
        """
        Create a DetailControl object
        """
        super(DetailControl, self).__init__(parent, kwargs)

class MasterControl(Control):
    """
    Control displaying detail about a selected item
    """

    def __init__(self, parent, **kwargs):
        """
        Create a MasterControl object
        """
        super(MasterControl, self).__init__(parent, **kwargs)
        self.detail = self.kwargs.get('levels')
        if self.detail:
            # Control is organized with a PanedWindow, either horizontally or vertically
            self.panedWindow = PanedWindow(self.parent, orient=self.detail.get('orientation', 'horizontal'))
            # Setup space for master control to be used in subclass
            self.masterSpace = Frame(self.panedWindow)
            self.panedWindow.add(self.masterSpace)
            # Setup detail control as a child to PanedWindow
            self.detailSpace = Frame(self.panedWindow)
            self.panedWindow.add(self.detailSpace)
            self.panedWindow.pack(fill=BOTH, expand=1, padx=STANDARD_PADDING, pady=STANDARD_PADDING)
            self.detailWidget = {}
        else:
            self.masterSpace = parent
            self.detailWidget = None
        self.currentDetailWidget = None

    def currentItem(self):
        raise NotImplementedError()

    def itemSelected(self, event):
        """
        Callback: an item was selected

        Shows detail information when an item is selected
        """
        if self.currentDetailWidget:
            self.currentDetailWidget.pack_forget()
        try:
            self.currentDetailWidget = self.detailWidget[self.currentItem()]
        except KeyError:
            pass
        else:
            self.currentDetailWidget.pack(fill=BOTH, expand=1, padx=STANDARD_PADDING, pady=STANDARD_PADDING)

    def reportDetail(self, item, message):
        widget = self.detailWidget.get(item)
        if not widget:
            widget = self.detailWidget[item] = Frame(self.detailSpace)
        if self.currentDetailWidget:
            self.currentDetailWidget.pack_forget()
        self.currentDetailWidget = widget
        widget.pack(fill=BOTH, expand=1, padx=STANDARD_PADDING, pady=STANDARD_PADDING)
        return widget

class Main(Control):
    """
    Main windows
    """

    tk = False

    def __init__(self, parent, **kwargs):
        """
        Create a Main object
        """
        assert parent is None, 'Main cannot have a parent'
        super(Main, self).__init__(parent, **kwargs)
        self.topics = {}

    def report(self, message, show=False):
        topic = self.messageTopic(message)
        if topic not in self.topics:
            w = Tk()
            w.title(topic)
            _Tk.register(w)
            try:
                status = self.kwargs['status'][topic]
                w.geometry(status['geometry'])
                status['_tla'] = time.time()
            except KeyError:
                pass
            w.protocol('WM_DELETE_WINDOW', partial(_Tk.stop))
            self.topics[topic] = w
        else:
            w = self.topics[topic]
            w.deiconify()
            w.attributes('-topmost', 1)
            #w.attributes('-alpha', .5)
            #w.attributes('-topmost', 0)
        return w

    def collectStatus(self):
        try:
            status = self.kwargs['status']
            tla = int(time.time())
            status.update(
                {
                    topic: dict(
                        geometry=widget.geometry(),
                        _tla=status.get('_tla', tla)
                    )
                    for topic, widget in self.topics.items()
                }
            )
        except KeyError:
            pass
        except AttributeError:
            pass

class Horizontal(Control):
    """
    Horizontal widget
    """

    def __init__(self, parent, topic, **kwargs):
        """
        Create a Horizontal object
        """
        super(Horizontal, self).__init__(parent, topic=topic, **kwargs)
        self.scrolled = ScrolledWindow(parent)
        self.scrolled.pack(fill=BOTH, expand=1)
        self.window = self.scrolled.subwidget('window')
        self.widget = PanedWindow(self.window, orient=HORIZONTAL)
        self.widget.pack(fill=BOTH, expand=1, padx=STANDARD_PADDING, pady=STANDARD_PADDING)
        self.topics = {}

    def report(self, message, show=False):
        """
        Report message

        :param message: event
        :type message: dict

        Adds a pane representing the topic
        """
        topic = self.messageTopic(message)
        if topic not in self.topics:
            w = Labelframe(self.widget, text=topic, padding=STANDARD_PADDING)
            try:
                status = self.kwargs['status'][topic]
                st = {k: v for k, v in status.items() if not k.startswith('_')}
                w.configure(st)
                status['_tla'] = time.time()
            except KeyError:
                pass
            self.widget.add(w)
            self.topics[topic] = w
        else:
            w = self.topics[topic]
        return w

    def collectStatus(self):
        try:
            status = self.kwargs['status']
            tla = int(time.time())
            status.update(
                {
                    topic: dict(
                        width=widget.winfo_width(),
                        height=widget.winfo_height(),
                        _tla=status.get('_tla', tla)
                    )
                    for topic, widget in self.topics.items()
                }
            )
        except KeyError:
            pass
        except AttributeError:
            pass

class Vertical(Control):
    """
    Vertical widget
    """

    def __init__(self, parent, topic, **kwargs):
        """
        Create a Vertical object
        """
        super(Vertical, self).__init__(parent, topic=topic, **kwargs)
        self.scrolled = ScrolledWindow(parent)
        self.scrolled.pack(fill=BOTH, expand=1)
        self.window = self.scrolled.subwidget('window')
        self.widget = PanedWindow(self.window, orient=VERTICAL)
        self.widget.pack(fill=BOTH, expand=1, padx=STANDARD_PADDING, pady=STANDARD_PADDING)
        self.topics = {}

    def report(self, message, show=False):
        """
        Report message

        :param message: event
        :type message: dict

        Adds a pane representing the topic
        """
        topic = self.messageTopic(message)
        if topic not in self.topics:
            w = Labelframe(self.widget, text=topic, padding=STANDARD_PADDING)
            try:
                status = self.kwargs['status'][topic]
                w.configure({k: v for k, v in status.items() if not k.startswith('_')})
                status['_tla'] = time.time()
            except KeyError:
                pass
            self.widget.add(w)
            self.topics[topic] = w
        else:
            w = self.topics[topic]
        return w

    def collectStatus(self):
        try:
            status = self.kwargs['status']
            tla = int(time.time())
            status.update(
                {
                    topic: dict(
                        width=widget.winfo_width(),
                        height=widget.winfo_height(),
                        _tla=status.get('_tla', tla)
                    )
                    for topic, widget in self.topics.items()
                }
            )
        except KeyError:
            pass
        except AttributeError:
            pass

class Notebook(Control):
    """
    Notebook widget
    """

    def __init__(self, parent, topic, **kwargs):
        """
        Create a Vertical object
        """
        super(Notebook, self).__init__(parent, topic=topic, **kwargs)
        self.widget = TkNotebook(parent, width=400, padding=STANDARD_PADDING)
        self.widget.pack(fill=BOTH, expand=1)
        self.topics = {}

    def report(self, message, show=False):
        """
        Report message

        :param message: event
        :type message: dict

        Adds a pane representing the topic
        """
        topic = self.messageTopic(message)
        if topic not in self.topics:
            w = Frame(self.widget)
            self.widget.add(w, text=topic + ' ', padding=STANDARD_PADDING)
            self.topics[topic] = w
        else:
            w = self.topics[topic]
            self.widget.select(w)
        return w

class List(MasterControl):
    """
    Simple list
    """

    def __init__(self, parent, **kwargs):
        """
        Create a List object
        """
        super(List, self).__init__(parent, **kwargs)
        self.widget = Scrolled(parent, Listbox, 'xy')
        self.widget.pack(fill=BOTH, expand=1)

    def report(self, message, show=False):
        """
        Report event

        :param message:
        :type message: dict
        """
        widget = self.widget.widget
        if 'format' in self.kwargs:
            widget.insert('end', self.kwargs['format'].format(**message))
        else:
            widget.insert('end', str(message))
        if show:
            widget.see(END)
            widget.selection_clear(0, END)  # XXX: Bug work around
            widget.selection_set(END, END)
        return self.widget

class Tree(MasterControl):
    """
    Tree
    """

    def __init__(self, parent, **kwargs):
        """
        Create a Tree object
        """
        super(Tree, self).__init__(parent, **kwargs)
        self.widget = Scrolled(self.masterSpace, Treeview, 'xy')
        self.widget.widget.bind('<<TreeviewSelect>>', self.itemSelected)
        self.widget.pack(fill=BOTH, expand=1)

    def currentItem(self):
        return self.widget.widget.focus()

    def report(self, message, show=False):
        """
        Report event

        :param message:
        :type message: dict
        """
        widget = self.widget.widget
        id = ''
        # Sort into topic cascade
        for t in [self.kwargs['topic']] + self.kwargs.get('sublevels', []):
            topic = message.get(t, UNSPECIFIED_TOPIC)
            try:
                id = next(i for i in widget.get_children(id) if widget.item(i, 'text') == topic)
            except StopIteration:
                id = widget.insert(id, 'end', text=topic)
            if show:
                widget.focus(id)
                widget.item(id, open=1)
                widget.see(id)
                widget.selection_set(id)
        if self.detail:
            return self.reportDetail(id, message)
        else:
            # Insert event
            if 'format' in self.kwargs:
                id = widget.insert(id, 'end', text=self.kwargs['format'].format(**message))
            else:
                id = widget.insert(id, 'end', text=str(message))
            if show:
                widget.see(id)
            return widget

class Form(DetailControl):
    """
    Form dialog
    """

    def __init__(self, parent, **kwargs):
        """
        Create a Form object
        """
        super(Form, self).__init__(parent, **kwargs)

    def report(self, message, show=False):
        pass
