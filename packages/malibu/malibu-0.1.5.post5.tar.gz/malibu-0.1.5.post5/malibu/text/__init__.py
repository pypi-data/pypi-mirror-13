# -*- coding: utf-8 -*-
import glob
import os


modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]


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
                obj.iteritems()}
    elif isinstance(obj, list):
        return [unicode2str(i) for i in obj]
    elif isinstance(obj, unicode):
        return obj.encode("utf-8")
    else:
        return obj
