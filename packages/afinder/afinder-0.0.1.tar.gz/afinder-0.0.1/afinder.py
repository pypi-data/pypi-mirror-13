# -*- coding:utf-8 -*-
"""
Afinder library
~~~~~~~~~~~~~~~~~~~~~
Afinder stands for attribute finder.
Afinder is an object attr or method find library, written in Python.
usage:
   >>> from afinder import afind
   >>> afind(obj, 'something')
   ['obj.attribute.something', 'obj.attribute.moha:something is here']
:copyright: (c) 2016 by Kapor Zhu.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'afinder'
__version__ = '0.0.1'
__author__ = 'Kapor Zhu'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Kapor Zhu'

import inspect
import re
import six

BASIC_TYPES = (six.string_types, float, complex, set) + six.integer_types


def _is_valid_member(name, value):
    internal_fields = (six._meth_func, six._meth_self, six._func_closure, six._func_code,
                       six._func_defaults, six._func_globals)
    return not name.startswith('__') and name not in internal_fields and not inspect.isclass(value) and not callable(value)


def _traversal_needed(value):
    types = (six.text_type, six.binary_type, set, float, complex,)
    return not isinstance(value, six.string_types) and not isinstance(value, six.integer_types) and not isinstance(value, types)


def _walk(obj):
    visited_ids = set()
    visited_ids.add(id(obj))
    fields = [('', name, value) for name, value in inspect.getmembers(obj)]
    while fields:
        next_level_fields = []
        for path, name, value in fields:
            if not _is_valid_member(name, value):
                continue
            path = '{}.{}'.format(path, name)
            if _traversal_needed(value):
                yield path, name, None
                if id(value) not in visited_ids:
                    if isinstance(value, (list, tuple)):
                        next_level_fields.extend([(path, str(i), v) for i, v in enumerate(value)])
                    elif isinstance(value, dict):
                        next_level_fields.extend([(path, str(k), v) for k, v in six.iteritems(value)])
                    else:
                        try:
                            iter(value)
                            # iterable
                            next_level_fields.extend([(path, str(i), v) for i, v in enumerate(value)])
                        except:
                            next_level_fields.extend([(path, n, v) for n, v in inspect.getmembers(value)])
                    visited_ids.add(id(value))
            else:
                 yield path, name, value
        fields = next_level_fields


def afind(obj, text):
    assert obj, 'obj is required'
    assert text, 'text is required'
    text_re = re.compile(text.lower(), re.I | re.M)
    paths = []
    for path, name, value in _walk(obj):
        if text_re.search(name):
            paths.append(path)
        elif value:
            try:
                if isinstance(value, six.text_type):
                    pass
                elif isinstance(value, six.string_types):
                    value = value.encode('utf-8', 'ignore')
                else:
                    value = six.text_type(value)
            except:
                pass

            if text_re.search(value):
                paths.append('{}:{}'.format(path, value.replace('\n', ' ')))
    return paths
