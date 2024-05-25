# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2018, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


'''
=============================================================
``fmtversion``:  Simple version variables for Python packages
=============================================================

:Author: Geoffrey M. Poore
:License: `BSD 3-Clause <http://opensource.org/licenses/BSD-3-Clause>`_

Converts version information into a string ``__version__`` and a namedtuple
``__version_info__`` suitable for Python packages.  The approach is inspired
by PEP 440 and ``sys.version_info``:

* https://www.python.org/dev/peps/pep-0440
* https://docs.python.org/3/library/sys.html

Versions of the form "major.minor.micro" are supported, with an optional,
numbered dev/alpha/beta/candidate/final/post status.  The module does not
support more complicated version numbers like "1.0b2.post345.dev456", since
this does not fit into a namedtuple of the form used by ``sys.version_info``.
The code is written as a single module, so that it may be bundled into
packages, rather than needing to be installed as a separate dependency.

Typical usage in a package's ``version.py`` with a bundled ``fmtversion.py``::

    from .fmtversion import get_version_plus_info
    __version__, __version_info__ = get_version_plus_info(1, 1, 0, 'final', 0)

Following ``sys.version_info``, ``get_version_plus_info()`` takes arguments
for a five-component version number:  major, minor, micro, releaselevel, and
serial.  The releaselevel may be any of dev, alpha, beta, candidate, final, or
post, or common variations/abbreviations thereof.  All arguments but
releaselevel must be convertable to integers.

If only ``__version__`` or ``__version_info__`` is desired, then the functions
``get_version()`` or ``get_version_info()`` may be used instead.  If a micro
version is not needed (``<major>.<minor>.<micro>``), then set the optional
keyword argument ``usemicro=False``.  This will omit a micro version from the
string ``__version__``, while the namedtuple ``__version_info__`` will still
have a field ``micro`` that is set to zero to simplify comparisons.  If each
releaselevel will only have one release, then set ``useserial=False``.  This
will omit a serial number from the string ``__version__``, while the
namedtuple ``__version_info__`` will still have a field ``serial`` that is set
to zero.

A function ``get_version_from_version_py_str()`` is included for extracting
the version from a ``version.py`` file that has been read into a string.  This
is intended for use in ``setup.py`` files.
'''




from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import sys
if sys.version_info.major == 2:
    str = basestring
import collections


# Version of this module, which will later be converted into a `__version__`
# and `__version_info__` once the necessary functions are created
__version_tuple__ = (1, 1, 0, 'final', 0)

__docformat__ = 'restructuredtext en'




VersionInfo = collections.namedtuple('VersionInfo', ['major', 'minor', 'micro',
                                                     'releaselevel', 'serial'])


def get_version_info(major, minor, micro, releaselevel, serial,
                     usemicro=True, useserial=True):
    '''
    Create a VersionInfo instance suitable for use as `__version_info__`.

    Perform all type and value checking that is needed for arguments; assume
    that no previous checks have been performed.  This allows all checks to be
    centralized in this single function.
    '''
    if not all(isinstance(x, int) or isinstance(x, str)
            for x in (major, minor, micro, serial)):
        raise TypeError('major, minor, micro, and serial must be integers or strings')
    if not isinstance(releaselevel, str):
        raise TypeError('releaselevel must be a string')
    if not all(isinstance(x, bool) for x in (usemicro, useserial)):
        raise TypeError('usemicro and useserial must be bools')

    try:
        major = int(major)
        minor = int(minor)
        micro = int(micro)
        serial = int(serial)
    except ValueError:
        raise ValueError('major, minor, micro, and serial must be convertable to integers')
    if any(x < 0 for x in (major, minor, micro, serial)):
        raise ValueError('major, minor, micro, and serial must correspond to non-negative integers')
    if not usemicro and micro != 0:
        raise ValueError('usemicro=False, but a micro value "{0}" has been set'.format(micro))
    if not useserial and serial != 0:
        raise ValueError('useserial=False, but a serial value "{0}" has been set'.format(serial))

    releaselevel_dict = {'dev': 'dev',
                         'a': 'a', 'alpha': 'a',
                         'b': 'b', 'beta': 'b',
                         'c': 'c', 'rc': 'c',
                         'candidate': 'c', 'releasecandidate': 'c',
                         'pre': 'c', 'preview': 'c',
                         'final': 'final',
                         'post': 'post', 'r': 'post', 'rev': 'post'}
    try:
        releaselevel = releaselevel_dict[releaselevel.lower()]
    except KeyError:
        raise ValueError('Invalid releaselevel "{0}"'.format(releaselevel))
    if releaselevel == 'final' and serial != 0:
        raise ValueError('final release must not have non-zero serial')

    return VersionInfo(major, minor, micro, releaselevel, serial)


def get_version(*args, **kwargs):
    '''
    Create a version string suitable for use as `__version__`.

    Make sure arguments are appropriate, but leave all actual processing and
    value and type checking to `get_version_info()`.
    '''
    usemicro = kwargs.pop('usemicro', True)
    useserial = kwargs.pop('useserial', True)
    if kwargs:
        raise TypeError('Unexpected keyword(s): {0}'.format(', '.join('{0}'.format(k) for k in kwargs)))

    if len(args) == 1:
        version_info = args[0]
        if not isinstance(version_info, VersionInfo):
            raise TypeError('Positional argument must have 5 components, or be a VersionInfo instance')
    elif len(args) == 5:
        version_info = get_version_info(*args, usemicro=usemicro, useserial=useserial)
    else:
        raise TypeError('Positional argument must have 5 components, or be a VersionInfo instance')

    version = '{0}.{1}'.format(version_info.major, version_info.minor)
    if usemicro:
        version += '.{0}'.format(version_info.micro)
    if version_info.releaselevel != 'final':
        if version_info.releaselevel in ('dev', 'post'):
                version += '.{0}'.format(version_info.releaselevel)
        else:
            version += '{0}'.format(version_info.releaselevel)
        if useserial:
            version += '{0}'.format(version_info.serial)

    return version


def get_version_plus_info(*args, **kwargs):
    '''
    Create a tuple consisting of a version string and a VersionInfo instance.
    '''
    usemicro = kwargs.pop('usemicro', True)
    useserial = kwargs.pop('useserial', True)
    if kwargs:
        raise TypeError('Unexpected keyword(s): {0}'.format(', '.join('{0}'.format(k) for k in kwargs)))

    version_info = get_version_info(*args, usemicro=usemicro, useserial=useserial)
    version = get_version(version_info, usemicro=usemicro, useserial=useserial)
    return (version, version_info)




# Now that the required functions exist, process `__version_tuple__` into
# `__version__` and `__version_info__` for the module
__version__, __version_info__ = get_version_plus_info(*__version_tuple__)





def get_version_from_version_py_str(string):
    '''
    Extract version from version.py that has been read into a string.

    This assumes a simple, straightforward version.py.  It is meant for use
    in setup.py files.
    '''
    if not isinstance(string, str):
        raise TypeError('Argument must be a string')
    if string.count('__version__') != 1:
        raise RuntimeError('Failed to extract version from string')
    exec_locals = {}
    for line in string.splitlines():
        if line.startswith('__version__'):
            if not any(x in line for x in ['get_version(', 'get_version_plus_info(']):
                raise RuntimeError('Failed to extract version from string')
            if 'fmtversion.get_version' in line:
                line = line.replace('fmtversion.get_version', 'get_version')
            try:
                exec(compile(line, 'version.py', 'exec'), globals(), exec_locals)
            except Exception:
                raise RuntimeError('Failed to extract version from string')
            break
    if '__version__' not in exec_locals:
        raise RuntimeError('Failed to extract version from string')
    return exec_locals['__version__']
