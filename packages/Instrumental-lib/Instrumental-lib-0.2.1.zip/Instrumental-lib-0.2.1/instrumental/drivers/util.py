# -*- coding: utf-8 -*-
# Copyright 2015 Nate Bogdanowicz
"""
Helpful utilities for wrapping libraries in Python
"""
from inspect import getargspec, isfunction
from functools import update_wrapper
import pint
from .. import Q_


def check_enum(enum_type, arg):
    """Checks if arg is an instance or key of enum_type, and returns that enum"""
    return arg if isinstance(arg, enum_type) else enum_type[arg]


def _cffi_wrapper(ffi, func, fname, arginfo, err_wrap, struct_maker, use_first_arg):
    argtypes = ffi.typeof(func).args
    n_expected_inargs = sum('in' in a for a in arginfo)

    def wrapped(self, *inargs):
        inargs = list(inargs)
        if use_first_arg and self._first_arg is not None:
            inargs.insert(0, self._first_arg)

        if len(inargs) != n_expected_inargs:
            message = '{}() takes '.format(fname)
            if n_expected_inargs == 0:
                message += 'no arguments'
            elif n_expected_inargs == 1:
                message += '1 argument'
            else:
                message += '{} arguments'.format(n_expected_inargs)

            message += ' ({} given)'.format(len(inargs))

            raise TypeError(message)

        outargs = []
        args = []
        buflen = None
        for info, argtype in zip(arginfo, argtypes):
            if 'inout' in info:
                inarg = inargs.pop(0)
                try:
                    inarg_type = ffi.typeof(inarg)
                except TypeError:
                    inarg_type = type(inarg)

                if argtype == inarg_type:
                    arg = inarg  # Pass straight through
                elif argtype.kind == 'pointer' and argtype.item.kind == 'struct':
                    arg = struct_maker(argtype, inarg)
                else:
                    arg = ffi.new(argtype, inarg)
                outargs.append((arg, lambda o: o[0]))
            elif 'in' in info:
                arg = inargs.pop(0)
            elif 'out' in info:
                if argtype.kind == 'pointer' and argtype.item.kind == 'struct':
                    arg = struct_maker(argtype)
                else:
                    arg = ffi.new(argtype)
                outargs.append((arg, lambda o: o[0]))
            elif info.startswith('buf'):
                if len(info) > 3:
                    buflen = int(info[3:])
                else:
                    buflen = self._buflen
                arg = ffi.new('char[]', buflen)
                outargs.append((arg, lambda o: ffi.string(o)))
            elif info == 'len':
                arg = buflen
                buflen = None
            else:
                raise Exception("Unrecognized arg info '{}'".format(info))
            args.append(arg)

        retval = func(*args)
        out_vals = [f(a) for a, f in outargs]

        if err_wrap:
            err_wrap(retval)
        else:
            out_vals.append(retval)

        if not out_vals:
            return None
        elif len(out_vals) == 1:
            return out_vals[0]
        else:
            return tuple(out_vals)

    wrapped.__name__ = fname
    return wrapped


class LibMeta(type):
    def __new__(metacls, clsname, bases, classdict):
        err_wrap = classdict['_err_wrap']
        prefix = classdict['_prefix']
        struct_maker = classdict['_struct_maker']
        ffi = classdict['_ffi']
        lib = classdict['_lib']

        classdict['_lib_funcs'] = {}

        for name, value in classdict.items():
            if not name.startswith('_') and not isfunction(value):
                flags = {'first_arg': True}
                if not isinstance(value, tuple):
                    value = (value,)

                if value and isinstance(value[-1], dict):
                    flags.update(value[-1])
                    value = value[:-1]
                func = _cffi_wrapper(ffi, getattr(lib, prefix + name), name, value, err_wrap,
                                     struct_maker, flags['first_arg'])
                func.__name__ = name
                func.__str__ = lambda self: "func " + self.__name__

                # Build func's repr string
                argtypes = ffi.typeof(getattr(lib, prefix + name)).args
                in_args = [a.cname for a, d in zip(argtypes, value) if 'in' in d]
                out_args = [a.item.cname for a, d in zip(argtypes, value)
                            if ('out' in d or 'buf' in d)]
                if flags['first_arg']:
                    in_args.pop(0)
                if not out_args:
                    out_args = ['None']
                repr_str = "{}({}) -> {}".format(name, ', '.join(in_args), ', '.join(out_args))

                # classdict[name] = func
                del classdict[name]
                classdict['_lib_funcs'][name] = (func, repr_str)  # HACK to get nice repr

        return super(LibMeta, metacls).__new__(metacls, clsname, bases, classdict)


class NiceLib(object):
    """Base class for mid-level library wrappers

    Provides a nice interface for quickly defining mid-level library wrappers. You define your own
    subclass for each specific library (DLL), then create an instance for each instance of your
    Instrument subclass. See the examples in the developer docs for more info.

    Attributes
    ----------
    _ffi
        FFI instance variable. Required.
    _lib
        FFI library opened with `dlopen()`. Required.
    _prefix : str, optional
        Prefix to strip from the library function names. E.g. If the library has functions named
        like ``SDK_Func()``, you can set `_prefix` to ``'SDK_'``, and access them as `Func()`.
    _first_arg : optional
        Object that will be automatically passed as the first argument to all library functions.
        Useful e.g. if you open a handle to an instrument, then need to pass that handle to all
        other subsequent functions. If a specific function does not take this argument, you should
        set its ``first_arg`` flag to *False*. In general, this first argument will only be
        automatically filled in if `_first_arg` is *None*.
    _err_wrap : function, optional
        Wrapper function to handle error codes returned by each library function.
    _struct_maker : function, optional
        Function that is called to create an FFI struct of the given type. Mainly useful for
        odd libraries that require you to always fill out some field of the struct, like its size
        in bytes (I'm looking at you PCO...)
    _buflen : int, optional
        The default length for buffers. This can be overridden on a per-argument basis in the
        argument's spec string, e.g `'buf64'` will make a 64-byte buffer.
    """
    __metaclass__ = LibMeta
    _err_wrap = None
    _prefix = ''
    _ffi = None  # MUST be filled in by subclass
    _lib = None  # MUST be filled in by subclass
    _struct_maker = None  # ffi.new
    _first_arg = None
    _buflen = 512

    def __init__(self, *args):
        # HACK to get nice repr
        class LibFunction(object):
            def __init__(fself, name, func, repr_str):
                fself._name = name
                fself._func = func
                fself._repr = repr_str

            def __call__(fself, *args):
                return fself._func(self, *args)

            def __str__(fself):
                return fself._repr

            def __repr__(fself):
                return fself._repr

        for name, (func, repr_str) in type(self)._lib_funcs.items():
            setattr(self, name, LibFunction(name, func, repr_str))


def check_units(*pos, **named):
    """Decorator to enforce the dimensionality of input args and return values
    """
    def inout_map(arg, unit_info, name=None):
        if unit_info is None:
            return arg

        optional, units = unit_info
        if optional and arg is None:
            return None
        else:
            q = Q_(arg)
            if q.dimensionality != units.dimensionality:
                if name is not None:
                    raise pint.DimensionalityError(q.units, units.units,
                                                   extra_msg=" for argument '{}'".format(name))
                else:
                    raise pint.DimensionalityError(q.units, units.units,
                                                   extra_msg=" for return value")
            return q

    return _unit_decorator(inout_map, inout_map, pos, named)


def unit_mag(*pos, **named):
    """Decorator to extract the magnitudes of input args and return values
    """
    def in_map(arg, unit_info, name):
        if unit_info is None:
            return arg

        optional, units = unit_info
        if optional and arg is None:
            return None
        else:
            q = Q_(arg)
            try:
                return q.to(units).magnitude
            except pint.DimensionalityError:
                raise pint.DimensionalityError(q.units, units.units,
                                               extra_msg=" for argument '{}'".format(name))

    def out_map(res, unit_info):
        if unit_info is None:
            return res

        optional, units = unit_info
        if optional and res is None:
            return None
        else:
            q = Q_(res)
            try:
                return q
            except pint.DimensionalityError:
                raise pint.DimensionalityError(q.units, units.units, extra_msg=" for return value")

    return _unit_decorator(in_map, out_map, pos, named)


def _unit_decorator(in_map, out_map, pos_args, named_args):
    def wrap(func):
        ret = named_args.pop('ret', None)

        if ret is None:
            ret_units = None
        elif isinstance(ret, tuple):
            ret_units = []
            for arg in ret:
                if arg is None:
                    unit = None
                elif isinstance(arg, basestring):
                    optional = arg.startswith('?')
                    if optional:
                        arg = arg[1:]
                    unit = (optional, Q_(arg))
                ret_units.append(unit)
            ret_units = tuple(ret_units)
        else:
            optional = ret.startswith('?')
            if optional:
                arg = ret[1:]
            ret_units = Q_(arg)

        arg_names, vargs, kwds, defaults = getargspec(func)

        pos_units = []
        for arg in pos_args:
            if arg is None:
                unit = None
            elif isinstance(arg, basestring):
                optional = arg.startswith('?')
                if optional:
                    arg = arg[1:]
                unit = (optional, Q_(arg))
            else:
                raise TypeError("Each arg spec must be a string or None")
            pos_units.append(unit)

        named_units = {}
        for name, arg in named_args.items():
            if arg is None:
                unit = None
            elif isinstance(arg, basestring):
                optional = arg.startswith('?')
                if optional:
                    arg = arg[1:]
                unit = (optional, Q_(arg))
            else:
                raise TypeError("Each arg spec must be a string or None")
            named_units[name] = unit

        # Add positional units to named units
        for i, units in enumerate(pos_units):
            name = arg_names[i]
            if name in named_units:
                raise Exception("Units of {} specified by position and by name".format(name))
            named_units[name] = units

        # Pad out the rest of the positional units with None
        pos_units.extend([None] * (len(arg_names) - len(pos_args)))

        # Add named units to positional units
        for name, units in named_units.items():
            try:
                i = arg_names.index(name)
                pos_units[i] = units
            except ValueError:
                pass

        defaults = tuple() if defaults is None else defaults

        # Convert the defaults
        new_defaults = {}
        ndefs = len(defaults)
        for d, u, n in zip(defaults, pos_units[-ndefs:], arg_names[-ndefs:]):
            new_defaults[n] = d if u is None else in_map(d, u, n)

        def wrapper(*args, **kwargs):
            # Convert the input arguments
            new_args = [in_map(a, u, n) for a, u, n in zip(args, pos_units, arg_names)]
            new_kwargs = {n: in_map(a, named_units.get(n, None), n) for n, a in kwargs.items()}

            # Fill in converted defaults
            for name in arg_names[max(len(args), len(arg_names)-len(defaults)):]:
                if name not in new_kwargs:
                    new_kwargs[name] = new_defaults[name]

            result = func(*new_args, **new_kwargs)

            # Allow for unit checking of multiple return values
            if isinstance(ret_units, tuple):
                return tuple(map(out_map, result, ret_units))
            else:
                return out_map(result, ret_units)
        update_wrapper(wrapper, func)
        return wrapper
    return wrap
