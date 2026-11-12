# -*- coding: utf-8 -*-
#
# Copyright (c) 2026
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#
# This module is loaded by the TeX-distribution launcher before any
# latexminted application modules.  Keep it standard-library-only.


import email.parser
import importlib.metadata
import re
import sys
import zipfile


_NAME_RE = re.compile(r'^\\s*([A-Za-z0-9][A-Za-z0-9._-]*)')
_VERSION_RE = re.compile(
    r'^v?(?P<release>\\d+(?:\\.\\d+)*)'
    r'(?:(?P<pre>a|b|rc)(?P<pre_n>\\d+))?'
    r'(?:\\.post(?P<post_n>\\d+))?'
    r'(?:\\.dev(?P<dev_n>\\d+))?$',
    re.IGNORECASE,
)
_SPECIFIER_RE = re.compile(r'^\\s*(>=|>|<=|<|==|!=)\\s*(\\S+)\\s*$')


def _version_key(version):
    match = _VERSION_RE.fullmatch(version)
    if match is None:
        raise ValueError('Unsupported version format')
    release = tuple(int(part) for part in match.group('release').split('.'))
    release = release + (0,) * (8 - len(release))
    if len(release) > 8:
        raise ValueError('Unsupported version format')
    pre = match.group('pre')
    post_n = match.group('post_n')
    dev_n = match.group('dev_n')
    if pre:
        phase = {'a': -3, 'b': -2, 'rc': -1}[pre.lower()]
        serial = int(match.group('pre_n'))
    elif post_n is not None:
        phase = 1
        serial = int(post_n)
    elif dev_n is not None:
        phase = -4
        serial = int(dev_n)
    else:
        phase = 0
        serial = 0
    # A development release sorts before the corresponding pre/post release.
    dev_order = 0 if dev_n is not None and (pre or post_n is not None) else 1
    return release, phase, serial, dev_order, int(dev_n or 0)


def _satisfies_specifier(version, specifier):
    if not specifier:
        return True
    for item in specifier.split(','):
        match = _SPECIFIER_RE.fullmatch(item)
        if match is None:
            # Unknown PEP 440 syntax is not a reason to risk mixing package
            # sources; let the launcher use its known bundled environment.
            return False
        operator, required_version = match.groups()
        try:
            actual = _version_key(version)
            required = _version_key(required_version)
        except (TypeError, ValueError):
            return False
        if operator == '>=' and not actual >= required:
            return False
        if operator == '>' and not actual > required:
            return False
        if operator == '<=' and not actual <= required:
            return False
        if operator == '<' and not actual < required:
            return False
        if operator == '==' and not actual == required:
            return False
        if operator == '!=' and not actual != required:
            return False
    return True


def _wheel_latexminted_version(wheel_paths):
    versions = []
    for wheel_path in wheel_paths:
        if not wheel_path.name.startswith('latexminted-'):
            continue
        with zipfile.ZipFile(wheel_path) as wheel:
            metadata_paths = [
                name for name in wheel.namelist()
                if name.endswith('.dist-info/METADATA')
            ]
            if len(metadata_paths) != 1:
                raise ValueError('Invalid latexminted wheel metadata')
            metadata = email.parser.Parser().parsestr(
                wheel.read(metadata_paths[0]).decode('utf-8')
            )
            if metadata.get('Name', '').lower().replace('_', '-') != 'latexminted':
                raise ValueError('Unexpected distribution in latexminted wheel')
            versions.append(metadata['Version'])
    if len(versions) != 1:
        raise ValueError('Could not identify exactly one latexminted wheel')
    return versions[0]


def _requirement_parts(requirement):
    # Environment markers and unsupported requirement syntax are handled
    # conservatively: the local environment is rejected and bundled instead.
    if ';' in requirement:
        raise ValueError('Environment markers are not supported by bootstrap')
    match = _NAME_RE.match(requirement)
    if match is None:
        raise ValueError('Invalid dependency requirement')
    name = match.group(1)
    remainder = requirement[match.end():].strip()
    if remainder.startswith('['):
        extra_end = remainder.find(']')
        if extra_end < 0:
            raise ValueError('Invalid dependency extras')
        remainder = remainder[extra_end + 1:].strip()
    return name, remainder


def local_installation_is_compatible(wheel_paths, *, debug=False, distribution_finder=None):
    """Return whether the active interpreter has a complete local installation.

    The bundled latexminted wheel defines the minimum acceptable library
    version.  The installed distribution's direct Requires-Dist entries
    define the dependency checks for that installed release.
    """
    if distribution_finder is None:
        distribution_finder = importlib.metadata.distribution
    try:
        minimum_version = _wheel_latexminted_version(wheel_paths)
        local_distribution = distribution_finder('latexminted')
        if _version_key(local_distribution.version) < _version_key(minimum_version):
            raise ValueError('Local latexminted is older than the bundled version')
        requirements = local_distribution.requires
        if requirements is None:
            requirements = []
        for requirement in requirements:
            name, specifier = _requirement_parts(requirement)
            dependency = distribution_finder(name)
            if not _satisfies_specifier(dependency.version, specifier):
                raise ValueError('Incompatible local dependency: ' + name)
    except Exception:
        if debug:
            print('latexminted: using bundled Python wheels', file=sys.stderr)
        return False
    if debug:
        print('latexminted: using local Python installation', file=sys.stderr)
    return True
