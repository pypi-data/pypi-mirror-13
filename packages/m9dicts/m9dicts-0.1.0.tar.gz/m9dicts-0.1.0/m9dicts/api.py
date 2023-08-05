#
# Copyright (C) 2011 - 2015 Red Hat, Inc.
# Copyright (C) 2011 - 2016 Satoru SATOH <ssato redhat.com>
# License: MIT
#
"""Functions operate on m9dicts objects.

.. versionchanged: 0.1.0

   - splitted / forked from python-anyconfig; old history was available in its
     mdict branch:
     https://github.com/ssato/python-anyconfig/blob/mdict/anyconfig/mergeabledict.py

"""
from __future__ import absolute_import

import collections
import functools
import operator
import re

import m9dicts.compat
import m9dicts.globals
import m9dicts.dicts
import m9dicts.utils


PATH_SEPS = ('/', '.')

_JSNP_GET_ARRAY_IDX_REG = re.compile(r"(?:0|[1-9][0-9]*)")
_JSNP_SET_ARRAY_IDX = re.compile(r"(?:0|[1-9][0-9]*|-)")

NAMEDTUPLE_CLS_KEY = "_namedtuple_cls_"


def _jsnp_unescape(jsn_s):
    """
    Parse and decode given encoded JSON Pointer expression, convert ~1 to
    / and ~0 to ~.

    .. note:: JSON Pointer: http://tools.ietf.org/html/rfc6901

    >>> _jsnp_unescape("/a~1b")
    '/a/b'
    >>> _jsnp_unescape("~1aaa~1~0bbb")
    '/aaa/~bbb'
    """
    return jsn_s.replace('~1', '/').replace('~0', '~')


def _split_path(path, seps=PATH_SEPS):
    """
    Parse path expression and return list of path items.

    :param path: Path expression may contain separator chars.
    :param seps: Separator char candidates.

    :return: A list of keys to fetch object[s] later.

    >>> _split_path('')
    []
    >>> _split_path('/')  # JSON Pointer spec expects this behavior.
    ['']
    >>> _split_path('/a') == _split_path('.a') == ['a']
    True
    >>> _split_path('a') == _split_path('a.') == ['a']
    True
    >>> _split_path('/a/b/c') == _split_path('a.b.c') == ['a', 'b', 'c']
    True
    >>> _split_path('abc')
    ['abc']
    """
    if not path:
        return []

    for sep in seps:
        if sep in path:
            if path == sep:  # Special case, '/' or '.' only.
                return ['']
            return [x for x in path.split(sep) if x]

    return [path]


def mk_nested_dic(path, val, seps=PATH_SEPS):
    """
    Make a nested dict iteratively.

    :param path: Path expression to make a nested dict
    :param val: Value to set
    :param seps: Separator char candidates

    >>> mk_nested_dic("a.b.c", 1)
    {'a': {'b': {'c': 1}}}
    >>> mk_nested_dic("/a/b/c", 1)
    {'a': {'b': {'c': 1}}}
    """
    ret = None
    for key in reversed(_split_path(path, seps)):
        ret = {key: val if ret is None else ret.copy()}

    return ret


def get(dic, path, seps=PATH_SEPS):
    """
    getter for nested dicts.

    :param dic: a dict[-like] object
    :param path: Path expression to point object wanted
    :param seps: Separator char candidates

    :return: A tuple of (result_object, error_message)

    >>> d = {'a': {'b': {'c': 0, 'd': [1, 2]}}, '': 3}
    >>> get(d, '/')  # key becomes '' (empty string).
    (3, '')
    >>> get(d, "/a/b/c")
    (0, '')
    >>> sorted(get(d, "a.b")[0].items())
    [('c', 0), ('d', [1, 2])]
    >>> (get(d, "a.b.d"), get(d, "/a/b/d/1"))
    (([1, 2], ''), (2, ''))
    >>> get(d, "a.b.key_not_exist")  # doctest: +ELLIPSIS
    (None, "'...'")
    >>> get(d, "/a/b/d/2")
    (None, 'list index out of range')
    >>> get(d, "/a/b/d/-")  # doctest: +ELLIPSIS
    (None, 'list indices must be integers...')
    """
    items = [_jsnp_unescape(p) for p in _split_path(path, seps)]
    if not items:
        return (dic, '')
    try:
        if len(items) == 1:
            return (dic[items[0]], '')

        parent = functools.reduce(operator.getitem, items[:-1], dic)

        if m9dicts.utils.is_list_like(parent) and \
                _JSNP_GET_ARRAY_IDX_REG.match(items[-1]):
            return (parent[int(items[-1])], '')
        else:
            return (parent[items[-1]], '')

    except (TypeError, KeyError, IndexError) as exc:
        return (None, str(exc))


def set_(dic, path, val, seps=PATH_SEPS):
    """
    setter for nested dicts.

    :param dic: a dict[-like] object support recursive merge operations
    :param path: Path expression to point object wanted
    :param seps: Separator char candidates

    >>> d = dict(a=1, b=dict(c=2, ))
    >>> set_(d, 'a.b.d', 3)
    >>> d['a']['b']['d']
    3
    """
    dic.update(mk_nested_dic(path, val, seps))


def make(obj=None, ordered=False, merge=m9dicts.globals.MS_DICTS,
         _ntpl_cls_key=NAMEDTUPLE_CLS_KEY, **options):
    """
    Factory function to create a dict-like object[s] supports merge operation
    from a dict or any other objects.

    :param obj: A dict or other object[s] or None
    :param ordered:
        Create an instance of OrderedMergeableDict instead of MergeableDict If
        it's True. Please note that OrderedMergeableDict class will be chosen
        for namedtuple objects regardless of this argument always to keep keys
        (fields) order.
    :param merge:
        Specify strategy from MERGE_STRATEGIES of how to merge results loaded
        from multiple configuration files.
    :param _ntpl_cls_key:
        Special keyword to embedded the class name of namedtuple object to the
        MergeableDict object created. It's a hack and not elegant but I don't
        think there are another ways to make same namedtuple object from the
        MergeableDict object created from it.
    """
    if merge not in m9dicts.globals.MERGE_STRATEGIES:
        raise ValueError("Wrong merge strategy: %r" % merge)

    cls = m9dicts.dicts.get_mdict_class(merge=merge, ordered=ordered)
    if obj is None:
        return cls()

    opts = dict(ordered=ordered, merge=merge, _ntpl_cls_key=_ntpl_cls_key)
    opts.update(options)

    if m9dicts.utils.is_dict_like(obj):
        return cls((k, None if v is None else make(v, **opts)) for k, v
                   in obj.items())
    elif m9dicts.utils.is_namedtuple(obj):
        ocls = m9dicts.dicts.get_mdict_class(merge=merge, ordered=True)
        mdict = ocls((k, make(getattr(obj, k), **opts)) for k in obj._fields)
        mdict[_ntpl_cls_key] = obj.__class__.__name__
        return mdict
    elif m9dicts.utils.is_list_like(obj):
        return type(obj)(make(v, **opts) for v in obj)
    else:
        return obj


def convert_to(obj, ordered=False, to_namedtuple=False,
               _ntpl_cls_key=NAMEDTUPLE_CLS_KEY, **opts):
    """
    Convert a dict-like object[s] support merge operation to a dict or
    namedtuple object recursively.

    Borrowed basic idea and implementation from bunch.unbunchify.
    (bunch is distributed under MIT license same as this module.)

    .. note::
       If `to_namedtuple` is True and given object `obj` is not a dict-like
       object keeping key orders , then the order of fields of result
       namedtuple object may be random and not stable.

    .. note::
       namedtuple object cannot have fields start with '_' because it may be
       conflicts with special methods of object like '__class__'. So it'll fail
       if to convert dicts has such keys.

    :param obj: A m9dicts objects or other primitive object
    :param ordered: Create an OrderedDict instead of dict to keep the key order
    :param to_namedtuple:
        Convert `obj` to namedtuple object of which definition is created on
        the fly if True instead of dict.
    :param _ntpl_cls_key:
        Special keyword to embedded the class name of namedtuple object to
        create.  See the comments in :func:`make` also.

    :return: A dict or namedtuple object if to_namedtuple is True
    """
    cls = m9dicts.compat.OrderedDict if ordered else dict
    if m9dicts.utils.is_dict_like(obj):
        if to_namedtuple:
            _name = obj.get(_ntpl_cls_key, "NamedTuple")
            _keys = [k for k in obj.keys() if k != _ntpl_cls_key]
            _vals = [convert_to(obj[k], to_namedtuple, _ntpl_cls_key,
                                **opts) for k in _keys]
            return collections.namedtuple(_name, _keys)(*_vals)
        else:
            return cls((k, convert_to(v, **opts)) for k, v in obj.items())
    elif m9dicts.utils.is_namedtuple(obj):
        if to_namedtuple:
            return obj  # Nothing to do if it's nested n.t. (it should be).
        else:
            return m9dicts.compat.OrderedDict((k, convert_to(getattr(obj, k),
                                                             ordered=True))
                                              for k in obj._fields)
    elif m9dicts.utils.is_list_like(obj):
        return type(obj)(convert_to(v, to_namedtuple, _ntpl_cls_key, **opts)
                         for v in obj)
    else:
        return obj

# vim:sw=4:ts=4:et:
