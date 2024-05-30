# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# https://opensource.org/license/BSD-3-clause
#


'''
# `fmtversion`:  Simple version variables for Python packages

Converts version information into a string `__version__` and a named tuple
`__version_info__` suitable for Python packages.  The approach is inspired
by PEP 440 and `sys.version_info`:

  * https://www.python.org/dev/peps/pep-0440

  * https://docs.python.org/3/library/sys.html

Versions of the form "major.minor.micro" are supported, with an optional,
numbered dev/alpha/beta/candidate/final/post status.  The module does not
support more complicated version numbers like "1.0b2.post345.dev456", since
this does not fit into a named tuple of the form used by `sys.version_info`.
The code is written as a single module, so that it may be bundled into
packages, rather than needing to be installed as a separate dependency.

Typical usage in a package's `version.py` with a bundled `fmtversion.py`:

```
from .fmtversion import get_version_plus_info
__version__, __version_info__ = get_version_plus_info(1, 2, 0, 'final', 0)
```

Following `sys.version_info`, `get_version_plus_info()` takes arguments
for a five-component version number:  major, minor, micro, release level, and
serial.  The release level may be any of dev, alpha, beta, candidate, final, or
post, or common variations/abbreviations thereof.  All arguments but
release level must be convertable to integers.

If only `__version__` or `__version_info__` is desired, then the functions
`get_version()` or `get_version_info()` may be used instead.  If a micro
version is not needed (`<major>.<minor>.<micro>`), then set the optional
keyword argument `usemicro=False`.  This will omit a micro version from the
string `__version__`, while the named tuple `__version_info__` will still
have a field `micro` that is set to zero to simplify comparisons.  If each
release level will only have one release, then set `useserial=False`.  This
will omit a serial number from the string `__version__`, while the
named tuple `__version_info__` will still have a field `serial` that is set
to zero.


## License

BSD 3-Clause License

Copyright (c) 2015-2024, Geoffrey M. Poore
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''




import collections


# Version of this module, which will later be converted into a `__version__`
# and `__version_info__` once the necessary functions are created
__version_tuple__ = (1, 2, 0, 'final', 0)




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
