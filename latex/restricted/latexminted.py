#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


'''
This Python executable is intended for installation within a TeX distribution,
along with Python wheels for the following Python packages:

  * latexminted:  https://pypi.org/project/latexminted/

  * latexrestricted:  https://pypi.org/project/latexrestricted/

  * latex2pydata:  https://pypi.org/project/latex2pydata/

  * Pygments:  https://pypi.org/project/Pygments/

The combined executable plus wheels provide everything that is needed for the
Python side of the minted LaTeX package.  No additional Python libraries are
required.

The wheels require Python >= 3.8.  If this executable is launched with an
earlier Python version, then it will attempt to locate a more recent Python
installation and run itself with that Python version in a subprocess.  The
search for more recent Python versions looks for executables of the form
`python3.x` on PATH.

If the latexminted Python package is installed separately, outside TeX, then
it will create a separate `latexminted` executable as part of the installation
process.  If this executable finds a suitable `latexminted` executable
elsewhere, outside a TeX installation, then this executable will run that
separate `latexminted` executable in a subprocess and exit.  This makes it
possible to install latexminted and dependencies separately and then customize
Pygments with additional packages that provide plugins.

Requirements for locating and running a separate `latexminted` executable:

  * Under Windows, the separate executable must be the first `latexminted.exe`
    found on PATH, or it must be the first `latexminted.exe` on PATH that is
    located under the user home directory.  Under other operating systems, the
    separate executable must be the first `latexminted` found on PATH.

  * The separate executable must be outside a TeX installation.  Under
    Windows, there is a check for `tex.exe` in the same directory as
    `latexminted.exe`.  Under all operating systems, there is a check for the
    case-insensitive strings "texlive", "miktex", and "tinytex" in the path to
    the `latexminted` executable.

  * The separate executable must be outside the current working directory,
    TEXMFOUTPUT, and TEXMF_OUTPUT_DIRECTORY.

  * The current directory, TEXMFOUTPUT, and TEXMF_OUTPUT_DIRECTORY cannot be
    subdirectories of the directory in which the executable is located.
'''


__version__ = '0.1.0b3'


import os
import pathlib
import platform
import shutil
import subprocess
import sys




# This is an abbreviated variant of `AnyPath` from latexrestricted:
# https://github.com/gpoore/latexrestricted/blob/main/latexrestricted/_anypath.py
class Path(type(pathlib.Path())):
    __slots__ = (
        '_cache_key',
    )

    if sys.version_info[:2] < (3, 9):
        def is_relative_to(self, other):
            try:
                self.relative_to(other)
                return True
            except ValueError:
                return False

    @property
    def cache_key(self):
        try:
            return self._cache_key
        except AttributeError:
            self._cache_key = (type(self), self)
            return self._cache_key

    _resolved_set = set()

    def resolve(self):
        resolved = super().resolve()
        self._resolved_set.add(resolved.cache_key)
        return resolved

    def is_resolved(self) -> bool:
        return self.cache_key in self._resolved_set


prohibited_path_roots = set()
prohibited_path_roots.add(Path.cwd())
env_TEXMFOUTPUT = os.getenv('TEXMFOUTPUT')
env_TEXMF_OUTPUT_DIRECTORY = os.getenv('TEXMF_OUTPUT_DIRECTORY')
for env_var in (env_TEXMFOUTPUT, env_TEXMF_OUTPUT_DIRECTORY):
    if env_var:
        env_var_path = Path(env_var)
        prohibited_path_roots.add(env_var_path)
        prohibited_path_roots.add(env_var_path.resolve())

def is_permitted_executable_path(executable_path, executable_path_resolved):
    if not executable_path_resolved.is_resolved():
        raise Exception('Second argument must be resolved path')
    if any(e.is_relative_to(p) or p.is_relative_to(e)
           for e in set([executable_path.parent, executable_path_resolved.parent])
           for p in prohibited_path_roots):
        return False
    return True

# TeX Live allows setting `TEXMFOUTPUT` in LaTeX configuration.
# Retrieving that value with kpsewhich follows the approach in latexrestricted:
# https://github.com/gpoore/latexrestricted/blob/main/latexrestricted/_latex_config.py
env_SELFAUTOLOC = os.getenv('SELFAUTOLOC')
env_TEXSYSTEM = os.getenv('TEXSYSTEM')
if not env_TEXMFOUTPUT and env_SELFAUTOLOC and (not env_TEXSYSTEM or env_TEXSYSTEM.lower() != 'miktex'):
    if platform.system() == 'Windows':
        # Make sure executable is *.exe, not *.bat or *.cmd:
        # https://docs.python.org/3/library/subprocess.html#security-considerations
        which_kpsewhich = shutil.which('kpsewhich.exe', path=env_SELFAUTOLOC)
    else:
        which_kpsewhich = shutil.which('kpsewhich', path=env_SELFAUTOLOC)
    if not which_kpsewhich:
        sys.exit(' '.join([
            'Environment variable SELFAUTOLOC has value "{}",'.format(env_SELFAUTOLOC),
            'but a "kpsewhich" executable was not found at that location',
        ]))
    which_kpsewhich_path = Path(which_kpsewhich)
    which_kpsewhich_resolved = which_kpsewhich_path.resolve()
    if not which_kpsewhich_resolved.name.lower().endswith('.exe'):
        sys.exit(' '.join([
            'Executable "kpsewhich" resolved to "{}",'.format(which_kpsewhich_resolved.as_posix()),
            'but *.exe is required',
        ]))
    if not is_permitted_executable_path(which_kpsewhich_path, which_kpsewhich_resolved):
        # As in the latexrestricted case, this doesn't initially check for the
        # TeX Live scenario where `TEXMFOUTPUT` is set in a `texmf.cnf` config
        # file to a location that includes the `kpsewhich` executable.  There
        # isn't a good way to get the value of `TEXMFOUTPUT` without running
        # `kpsewhich` in that case.
        sys.exit(
            'Executable "kpsewhich" is located under the current directory, TEXMFOUTPUT, or '
            'TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory as the executable'
        )
    kpsewhich_cmd = [which_kpsewhich_resolved.as_posix(), '--var-value', 'TEXMFOUTPUT']
    try:
        kpsewhich_proc = subprocess.run(kpsewhich_cmd, shell=False, capture_output=True)
    except PermissionError:
        sys.exit('Insufficient permission to run "{}"'.format(which_kpsewhich_resolved.as_posix()))
    kpsewhich_TEXMFOUTPUT = kpsewhich_proc.stdout.decode(sys.stdout.encoding) or None
    if kpsewhich_TEXMFOUTPUT:
        kpsewhich_TEXMFOUTPUT_path = Path(kpsewhich_TEXMFOUTPUT)
        prohibited_path_roots.add(kpsewhich_TEXMFOUTPUT_path)
        prohibited_path_roots.add(kpsewhich_TEXMFOUTPUT_path.resolve())
    if not is_permitted_executable_path(which_kpsewhich_path, which_kpsewhich_resolved):
        # It is now possible to check for the TeX Live scenario where
        # `TEXMFOUTPUT` is set in a `texmf.cnf` config file to a location that
        # includes the `kpsewhich` executable.  Giving an error message after
        # already running `kpsewhich` isn't ideal, but there isn't a good
        # alternative.  As in the latexrestricted case, the impact on overall
        # security is negligible because an unsafe value of `TEXMFOUTPUT`
        # means that all TeX-related executables are potentially compromised.
        sys.exit(
            'Executable "kpsewhich" is located under the current directory, TEXMFOUTPUT, or '
            'TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory as the executable'
        )


if sys.version_info[:2] < (3, 8):
    for minor_version in range(13, 7, -1):
        if platform.system() == 'Windows':
            # Batch files must be prohibited:
            # https://docs.python.org/3/library/subprocess.html#security-considerations
            which_python = shutil.which('python3.{}.exe'.format(minor_version))
        else:
            which_python = shutil.which('python3.{}'.format(minor_version))
        if which_python:
            which_python_path = Path(which_python)
            which_python_resolved = which_python_path.resolve()
            if platform.system() == 'Windows' and not which_python_resolved.name.lower().endswith('.exe'):
                continue
            if is_permitted_executable_path(which_python_path, which_python_resolved):
                python_cmd = [which_python_resolved.as_posix(), __file__] + sys.argv[1:]
                python_proc = subprocess.run(python_cmd, shell=False, capture_output=True)
                sys.stderr.buffer.write(python_proc.stderr)
                sys.stdout.buffer.write(python_proc.stdout)
                sys.exit(python_proc.returncode)
    sys.exit('latexminted requires Python >= 3.8, but a compatible Python executable was not found on PATH')


script_resolved = Path(__file__).resolve()
required_wheel_packages = (
    'latexminted',
    'latexrestricted',
    'latex2pydata',
    'pygments',
)
wheel_paths = [p for p in script_resolved.parent.glob('*.whl') if p.name.startswith(required_wheel_packages)]
if not wheel_paths:
    sys.exit('latexminted failed to find bundled wheels *.whl')
for pkg in required_wheel_packages:
    if not any(whl.name.startswith(pkg) for whl in wheel_paths):
        sys.exit('latexminted failed to find all required bundled wheels *.whl')
for wheel_path in wheel_paths:
    sys.path.insert(0, wheel_path.as_posix())


if platform.system() == 'Windows':
    which_latexminted = shutil.which('latexminted.exe')
    windows_fallback_path_search = True
else:
    which_latexminted = shutil.which('latexminted')
    windows_fallback_path_search = False
if which_latexminted:
    which_latexminted_path = Path(which_latexminted)
    which_latexminted_resolved = which_latexminted_path.resolve()
    if platform.system() == 'Windows' and not which_latexminted_resolved.name.lower().endswith('.exe'):
        sys.exit(' '.join([
            'Executable "latexminted" resolved to "{}",'.format(which_latexminted_resolved.as_posix()),
            'but *.exe is required',
        ]))
    if which_latexminted_resolved == script_resolved:
        pass
    elif platform.system() == 'Windows' and (which_latexminted_resolved.parent / 'tex.exe').exists():
        pass
    elif any(x in which_latexminted_resolved.as_posix().lower() for x in ('texlive', 'miktex', 'tinytex')):
        pass
    elif is_permitted_executable_path(which_latexminted_path, which_latexminted_resolved):
        latexminted_cmd = [which_latexminted_resolved.as_posix()] + sys.argv[1:]
        latexminted_proc = subprocess.run(latexminted_cmd, shell=False, capture_output=True)
        sys.stderr.buffer.write(latexminted_proc.stderr)
        sys.stdout.buffer.write(latexminted_proc.stdout)
        sys.exit(latexminted_proc.returncode)
    else:
        # Under Windows, if there was a `latexminted` executable on PATH
        # outside a TeX installation, but it wasn't permitted due to its
        # location, don't perform fallback search.
        windows_fallback_path_search = False
if windows_fallback_path_search:
    # Windows appends user PATH to system PATH, so the system PATH may prevent
    # finding a user installation of `latexminted`.  Search through PATH
    # elements under user home directory to check for `latexminted.exe`
    # outside a TeX installation.
    home_path = Path.home()
    env_PATH = os.environ.get('PATH', '')
    for path_elem in env_PATH.split(os.pathsep):
        if not path_elem or not Path(path_elem).is_relative_to(home_path):
            continue
        which_latexminted = shutil.which('latexminted.exe', path=path_elem)
        if not which_latexminted:
            continue
        which_latexminted_path = Path(which_latexminted)
        which_latexminted_resolved = which_latexminted_path.resolve()
        if which_latexminted_resolved == script_resolved:
            break
        elif (which_latexminted_resolved.parent / 'tex.exe').exists():
            break
        elif any(x in which_latexminted_resolved.as_posix().lower() for x in ('texlive', 'miktex', 'tinytex')):
            break
        elif is_permitted_executable_path(which_latexminted_path, which_latexminted_resolved):
            latexminted_cmd = [which_latexminted_resolved.as_posix()] + sys.argv[1:]
            try:
                latexminted_proc = subprocess.run(latexminted_cmd, shell=False, capture_output=True)
            except PermissionError:
                break
            sys.stderr.buffer.write(latexminted_proc.stderr)
            sys.stdout.buffer.write(latexminted_proc.stdout)
            sys.exit(latexminted_proc.returncode)
        else:
            break


from latexminted.cmdline import main
main()
