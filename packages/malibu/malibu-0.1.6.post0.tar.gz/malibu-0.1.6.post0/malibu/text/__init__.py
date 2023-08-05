# -*- coding: utf-8 -*-
from __future__ import print_function

import glob
import os


modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]


def unicode_type():
    """ Find the Unicode class for this version of Python.
        Between Python 2.x and 3.x, classes and text handling has
        changed a considerable amount.
        Python 2.x uses ASCII strings with str() and Unicode with
        unicode().
        Python 3.x uses Unicode strings with str() and "strings of
        bytes" as bytes().
    """

    try:
        import builtins
        __old_unicode = False
    except ImportError:
        __old_unicode = True

    if __old_unicode:
        return unicode  # flake8: noqa
    elif not __old_unicode:
        return str  # flake8: noqa


def string_type():
    """ Find the String class for this version of Python.
        Between Python 2.x and 3.x, classes and text handling has
        changed a considerable amount.
        Python 2.x uses ASCII strings with str() and Unicode with
        unicode().
        Python 3.x uses Unicode strings with str() and "strings of
        bytes" as bytes().
    """

    try:
        import builtins
        __old_string = True
    except ImportError:
        __old_string = False

    if __old_string:
        return str  # flake8: noqa
    elif not __old_string:
        return bytes  # flake8: noqa


def unicode2str(obj):
    """ Recursively convert an object and members to str objects
        instead of unicode objects, if possible.

        This only exists because of the incoming world of unicode_literals.

        :param object obj: object to recurse
        :return: object with converted values
        :rtype: object
    """

    if isinstance(obj, dict):
        return {unicode2str(k): unicode2str(v) for k, v in
                obj.items()}
    elif isinstance(obj, list):
        return [unicode2str(i) for i in obj]
    elif isinstance(obj, unicode_type()):
        return obj.encode("utf-8")
    else:
        return obj


def str2unicode(obj, encoding='utf-8'):
    """ Recursively convert an object and members to unicode objects
        instead of str objects, if possible.

        This only exists because of the incoming world of unicode_literals.

        :param object obj: object to recurse
        :param str encoding: encoding to decode from
        :return: object with converted values
        :rtype: object
    """

    if isinstance(obj, dict):
        return {str2unicode(k): str2unicode(v) for k, v in
                obj.items()}
    elif isinstance(obj, list):
        return [str2unicode(i) for i in obj]
    elif isinstance(obj, string_type()):
        return obj.decode(encoding)
    else:
        return obj
