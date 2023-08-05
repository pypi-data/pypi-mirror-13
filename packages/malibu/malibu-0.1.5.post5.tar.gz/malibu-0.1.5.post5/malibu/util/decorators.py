# -*- coding: utf-8 -*-
""" This module contains decorator generators.
    Essentially this will be a medley of delicious functions
    to generate relatively useful, reusable, generic decorators for code.
"""


def function_registrator(target):
    """ function_registrator generates a simple decorator that will
        take a function with any set of arguments and register that
        function within a target list.
    """

    def decorator(func):
        """ This is a "flexible" decorator function that pushes to
            target thanks to scope magic.
        """

        if func not in target:
            target.append(func)

        return func

    return decorator


def function_marker(attr, value):
    """ function marker generates a simple decorator that will
        take a function with any set of arguments and set a given
        attribute on that function with setattr().
    """

    def decorator(func):
        """ This is a "flexible" decorator function that sets the
            attribute on the target function.
        """

        setattr(func, attr, value)

        return func

    return decorator


def function_kw_reg(target, req_args):
    """ function kw reg generates a more complex decorator that
        must be used with the argument names given in req_args.
        useful for attribute-based assertion.

        NOTE: target should be a dict-typed class

        example:

            trait = function_kw_reg(target, ['val1', 'val2', 'val3'])

            @trait(val1 = "attr1", val2 = "attr2", val3 = "attr3")
            def do_thing(...):
                pass
    """

    def decorator_outer(**kw):

        for req in req_args:
            if req not in kw.keys():
                raise KeyError("Missing required attribute: %s" % (req))

        def decorator(func):

            if func not in target:
                target.update({func: kw})

            return func

        return decorator

    return decorator_outer
