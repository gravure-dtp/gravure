#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Atelier Obscur.
# Authors:
# Gilles Coissac <gilles@atelierobscur.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License with
# the Debian GNU/Linux distribution in file /usr/share/common-licenses/GPL;
# if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA 02110-1301, USA.

__all__ = ['MatrixView', 'CellViewer']


import sys
from gi.repository import Gtk
from gi.repository import GObject

from abc import *

from halftone import spotfunctions
from halftone.base import *


class ArrayInterface(metaclass=ABCMeta):
    """ArrayInterface.

    http://docs.scipy.org/doc/numpy/reference/arrays.interface.html#\
__array_interface__

    """

    class __ArrayInterface():
        """A dictionary of items (3 required and 5 optional).

        The optional keys in the dictionary have implied defaults if they are
        not provided.

        The keys are:


        shape (required)

        Tuple whose elements are the array size in each dimension.
        Each entry is an integer (a Python int or long). Note that these
        integers could be larger than the platform “int” or “long” could hold
        (a Python int is a C long). It is up to the code using this attribute
        to handle this appropriately; either by raising an error when
        overflow is possible, or by using Py_LONG_LONG as the C type
        for the shapes.


        typestr (required)

        A string providing the basic type of the homogenous array
        The basic string format consists of 3 parts: a character describing
        the byteorder of the data (<: little-endian, >: big-endian,
        |: not-relevant), a character code giving the basic type of
        the array, and an integer providing the number of bytes the type
        uses. The basic type character codes are:

        t	Bit field (following integer gives the number of bits
            in the bit field).
        b	Boolean (integer type where all values are only True or False)
        i	Integer
        u	Unsigned integer
        f	Floating point
        c	Complex floating point
        O	Object (i.e. the memory contains a pointer to PyObject)
        S	String (fixed-length sequence of char)
        U	Unicode (fixed-length sequence of Py_UNICODE)
        V	Other (void * – each item is a fixed-size chunk of memory)


        descr (optional)

        A list of tuples providing a more detailed description of the memory
        layout for each item in the homogeneous array. Each tuple in the list
        has two or three elements. Normally, this attribute would be used
        when typestr is V[0-9]+, but this is not a requirement.
        The only requirement is that the number of bytes represented in the
        typestr key is the same as the total number of bytes represented
        here. The idea is to support descriptions of C-like structs (records)
        that make up array elements. The elements of each tuple
        in the list are:

        1 A string providing a name associated with this portion of the
          record. This could also be a tuple of ('full name', 'basic_name')
          where basic name would be a valid Python variable name representing
          the full name of the field.
        2 Either a basic-type description string as in typestr or another
          list (for nested records).
        3 An optional shape tuple providing how many times this part of the
          record should be repeated. No repeats are assumed if this is not
          given. Very complicated structures can be described using this
          generic interface. Notice, however, that each element of the array
          is still of the same data-type. Some examples of using this
          interface are given below.

        Default: [('', typestr)]


        data (optional)

        A 2-tuple whose first argument is an integer (a long integer if
        necessary) that points to the data-area storing the array contents.
        This pointer must point to the first element of data (in other words
        any offset is always ignored in this case). The second entry in the
        tuple is a read-only flag (true means the data area is read-only).

        This attribute can also be an object exposing the buffer interface
        which will be used to share the data. If this key is not present
        (or returns None), then memory sharing will be done through the
        buffer interface of the object itself. In this case, the offset key
        can be used to indicate the start of the buffer. A reference to the
        object exposing the array interface must be stored by the new object
        if the memory area is to be secured.

        Default: None


        strides (optional)

        Either None to indicate a C-style contiguous array or a Tuple of
        strides which provides the number of bytes needed to jump to the next
        array element in the corresponding dimension. Each entry must be an
        integer (a Python int or long). As with shape, the values may be
        larger than can be represented by a C “int” or “long”; the calling
        code should handle this appropiately, either by raising an error,
        or by using Py_LONG_LONG in C. The default is None which implies
        a C-style contiguous memory buffer. In this model, the last dimension
        of the array varies the fastest. For example, the default strides
        tuple for an object whose array entries are 8 bytes long and whose
        shape is (10,20,30) would be (4800, 240, 8)

        Default: None (C-style contiguous)


        mask (optional)

        None or an object exposing the array interface. All elements of
        the mask array should be interpreted only as true or not true
        indicating which elements of this array are valid. The shape of this
        object should be “broadcastable” to the shape of the original array.

        Default: None (All array values are valid)


        offset (optional)

        An integer offset into the array data region. This can only be used
        when data is None or returns a buffer object.

        Default: 0.


        version (required)

        An integer showing the version of the interface (i.e. 3 for this
        version). Be careful not to use this to invalidate objects exposing
        future versions of the interface.

        """
        instance_dict = {}
        def __get__(self, instance, cls):
            if instance is not None:
                return __ArrayInterface.instance_dict[id(instance)]
            else :
                return AttributError()


    __array_interface__ = __ArrayInterface()

    def __new__(cls):
        self = super().__new__(cls)
        ArrayInterface.__ArrayInterface.instance_dict[id(self)] =\
                        {'shape':NotImplemented,
                         'typestr':NotImplemented,
                         'version':3,
                         'descr':[('', 'typestr')],  #FIXME: typestr
                         'data':None,
                         'strides':None,
                         'mask':None,
                         'offset':0}
        return self

    @abstractproperty
    def ndim(self):
        """Number of array dimensions.
        """
        return len(self.__array_interface__['shape'])

    @abstractproperty
    def shape(self):
        """Tuple of integers whose elements are the array size\
in each dimension.
        """
        return self.__array_interface__['shape']

    @abstractproperty
    def itemsize(self):
        """Length of one array element in bytes.
        """
        return int(self.__array_interface__['typestr'][-1:])

    @abstractproperty
    def strides(self):
        """Tuple of integers giving the size in bytes to step in each\
dimension when traversing an array.
        """
        return self.__array_interface__['strides']

    @abstractproperty
    def size(self):
        r = 1
        for e in self.shape:
            r *= e
        return r

    @abstractmethod
    def tolist(self):
        return NotImplementedError

    @classmethod
    def __subclasshook__(cls, sbcls):
        if cls is ArrayInterface:
            if hasattr(sbcls, '__array_interface__') or \
               (hasattr(sbcls, 'ndim') and \
                hasattr(sbcls, 'shape') and \
                hasattr(sbcls, 'itemsize') and \
                hasattr(sbcls, 'strides') and \
                hasattr(sbcls, 'tolist')):
                return True
            else:
                return False
        return NotImplemented


import numpy as np
ArrayInterface.register(np.ndarray)
x = np.array([[1, 2, 3], [4, 5, 6]], np.int32)
print('numpy ndarray have AI:', isinstance(x, ArrayInterface))
m = memoryview(b'abcd')
print('memoryview have AI:', isinstance(m, ArrayInterface))
help(ArrayInterface)



class MatrixView(Gtk.DrawingArea, Gtk.Scrollable):
    """A scrollable Gtk widget for making graphical representation\
    of 2D matrix (in sense of raster object).

    Extends Gtk.DrawingArea and implements Gtk.Scrollable.
    """

    hscroll_policy = GObject.property(type=Gtk.ScrollablePolicy,
                                      default=Gtk.ScrollablePolicy.MINIMUM,
                                      flags=GObject.PARAM_READWRITE)
    vscroll_policy = GObject.property(type=Gtk.ScrollablePolicy,
                                      default=Gtk.ScrollablePolicy.MINIMUM,
                                      flags=GObject.PARAM_READWRITE)

    def set_hadjustment(self, value):
        setattr(MatrixView.hadjustment, '_property_helper_hadjustment', value)
        self.hadjustment.set_page_increment(5)
        self.hadjustment.set_step_increment(1)
        self.hadjustment.connect('value-changed', self._on_hscroll)

    def get_hadjustment(self):
        return getattr(MatrixView.hadjustment, '_property_helper_hadjustment')

    hadjustment = GObject.property(type=Gtk.Adjustment,
                                   default=None,
                                   setter=set_hadjustment,
                                   getter=get_hadjustment,
                                   flags=GObject.PARAM_READWRITE)

    def set_vadjustment(self, value):
        setattr(MatrixView.vadjustment, '_property_helper_vadjustment', value)
        self.vadjustment.set_page_increment(5)
        self.vadjustment.set_step_increment(1)
        self.vadjustment.connect('value-changed', self._on_vscroll)

    def get_vadjustment(self):
        return getattr(MatrixView.vadjustment, '_property_helper_vadjustment')

    vadjustment = GObject.property(type=Gtk.Adjustment,
                                   default=None,
                                   setter=set_vadjustment,
                                   getter=get_vadjustment,
                                   flags=GObject.PARAM_READWRITE)

    hsize = GObject.property(type=int,
                             flags=GObject.PARAM_READWRITE,
                             default=1,
                             minimum=1,
                             maximum=8000)

    vsize = GObject.property(type=int,
                             flags=GObject.PARAM_READWRITE,
                             default=1,
                             minimum=1,
                             maximum=8000)

    scale = GObject.property(type=float,
                             flags=GObject.PARAM_READWRITE,
                             default=1.0,
                             minimum=1.0)

    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value

    data = property(fget=get_data, fset=set_data)

    def __init__(self, data=None):
        Gtk.DrawingArea.__init__(self)
        self.data = data
        self.connect('draw', self._on_draw_cb)

    def set_size(self, h, v):
        self.hsize, self.vsize = h, v

    def get_size(self):
        return self.hsize, self.vsize

    def _on_hscroll(self, adjustment):
        self.data = 'scroll'
        print("H scroll", adjustment.get_value())

    def _on_vscroll(self, adjustment):
        print("V scroll", adjustment.get_value())

    def _on_draw_cb(self, widget, ctx):
        w = self.get_allocated_width()
        h = self.get_allocated_height()

        self.hadjustment.set_page_size(w)
        self.hadjustment.set_lower(1)
        self.hadjustment.set_upper(1000)

        self.vadjustment.set_page_size(h)
        self.vadjustment.set_lower(1)
        self.vadjustment.set_upper(1000)

        print('h_page_size', self.hadjustment.get_page_size())
        print('h_value', self.hadjustment.get_value())
        print('h_upper', self.hadjustment.get_upper())
        print('h_step', self.hadjustment.get_step_increment())

        self._draw_background(ctx, w, h)
        self._draw_bounding_box(ctx, w, h)

        print('w,h: ', w, h)

        return True

    def _draw_background(self, ctx, w, h):
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgba(0, 0, 0.5)
        ctx.fill()

    def _draw_bounding_box(self, ctx, w, h):
        ctx.rectangle(50, 50, 100, 100)
        ctx.set_source_rgba(0.5, 0.5, 0.5)
        ctx.fill()


class CellViewer(Gtk.Window):

    def __init__(self, cell, title="Cell view", application=None):
        if not isinstance(cell, Cell):
            raise AttributeError("cell should be an halfone.base.Cell Type")
        Gtk.Window.__init__(self, application=application)

        # Attributes
        self.cell = cell
        scroll_win = Gtk.ScrolledWindow()
        self.add(scroll_win)
        self.draw_area = MatrixView()
        scroll_win.add(self.draw_area)

        # window setting
        self.set_title(title)
        self.set_default_size(400, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()


class App(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        self.test()

    def test(self):
        spot_f = spotfunctions.Rhomboid()
        self.h_cell = Cell(93, 93)
        self.topwin = CellViewer(self.h_cell, application=self)
        self.h_cell.setBuildOrder(BuildOrderSpotFunction(spot_f))
        self.h_cell.fill()

        print(spot_f)
        print(self.h_cell)
        #self.topwin.plotWhiteningOrder()

    def do_activate(self):
        self.topwin.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


def main():
    exit_code = App().run(sys.argv)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
