#
# Copyright 2008-2014 Universidad Complutense de Madrid
#
# This file is part of Numina
#
# Numina is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Numina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Numina.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Recipe requirements
"""

import inspect

from .types import NullType, PlainPythonType
from .types import ListOfType


class EntryHolder(object):
    def __init__(self, tipo, description, destination, optional,
                 default, choices=None, validation=True):

        super(EntryHolder, self).__init__()

        if tipo is None:
            self.type = NullType()
        elif tipo in [bool, str, int, float, complex, list]:
            self.type = PlainPythonType(ref=tipo())
        elif isinstance(tipo, ListOfType):
            self.type = tipo
        elif inspect.isclass(tipo):
            self.type = tipo()
        else:
            self.type = tipo

        self.description = description
        self.optional = optional
        self.dest = destination
        self.default = default
        self.choices = choices
        self.validation = validation

    def __get__(self, instance, owner):
        """Getter of the descriptor protocol."""
        if instance is None:
            return self
        else:
            if self.dest not in instance._numina_desc_val:
                instance._numina_desc_val[self.dest] = self.default_value()

            return instance._numina_desc_val[self.dest]

    def __set__(self, instance, value):
        """Setter of the descriptor protocol."""
        cval = self.convert(value)
        if self.choices and (cval not in self.choices):
            raise ValueError('{} not in {}'.format(cval, self.choices))
        instance._numina_desc_val[self.dest] = cval

    def convert(self, val):
        return self.type.convert(val)

    def validate(self, val):
        if self.validation:
            return self.type.validate(val)
        return True

    def default_value(self):
        if self.default is not None:
            return self.convert(self.default)
        if self.type.default is not None:
            return self.type.default
        if self.optional:
            return None
        else:
            fmt = 'Required {0!r} of type {1!r} is not defined'
            msg = fmt.format(self.dest, self.type)
            raise ValueError(msg)


class Product(EntryHolder):
    '''Product holder for RecipeResult.'''
    def __init__(self, ptype, description='', validation=True,
                 dest=None, optional=False, default=None, *args, **kwds):
        super(Product, self).__init__(
            ptype, description, dest, optional,
            default, choices=None, validation=validation
            )

#        if not isinstance(self.type, DataProductType):
#            raise TypeError('type must be of class DataProduct')

    def __repr__(self):
        return 'Product(type=%r, dest=%r)' % (self.type, self.dest)
