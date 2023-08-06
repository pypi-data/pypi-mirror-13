#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

class ObjectDict(dict):

    """
    An object that is usable as a dict or an object.

    .. code-block:: python

        o = ObjectDict()
        o.key = 'value'
        print(o['key'])
        'value'
    """

    def __init__(self, dictionary=None):
        dict.__init__(self)

        if dictionary is None:
            dictionary = dict()

        for key, value in dictionary.items():
            setattr(self, key, value)

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = ObjectDict(value)
        dict.__setitem__(self, name, value)

    def __getattr__(self, name):
        """Emulate the attribute with the dict key."""
        if name in self:
            return dict.__getitem__(self, name)
        else:
            raise AttributeError(name)

    def __delattr__(self, name):
        """Emulate the attribute with the dict key."""
        if name in self:
            dict.__delitem__(self, name)
        else:
            raise AttributeError(name)

    __setitem__ = __setattr__
