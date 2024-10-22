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
process.  That makes it possible to install latexminted and dependencies
separately and then customize Pygments with additional packages that provide
plugins.  However, running that separate `latexminted` executable is not
straightforward under Windows.  Under Windows, if this executable finds a
suitable `latexminted` executable elsewhere, outside a TeX installation, then
this executable will run that separate `latexminted` executable in a
subprocess and exit.  There are two reasons for this approach:

 1. Under Windows with TeX Live, the default restricted shell escape can only
    run executables such as `latexminted` that are part of the TeX
    installation; the executable that runs is not the first executable on
    PATH.  That is part of TeX Live's security measures to prevent running
    executables in the current working directory, which is typically writable
    by LaTeX and is the first place Windows checks when searching for
    executables.  This script and the latexrestricted Python package enforce
    equivalent security, but do so in a less restrictive manner by expanding
    executable names into executable paths with Python's `shutil.which()` and
    then comparing the result with locations writable by LaTeX.

 2. Under non-Windows operating systems, it is possible to modify PATH so that
    the desired `latexminted` executable is first.  Under Windows, the system
    PATH is prepended to the user PATH, so a system-wide TeX installation will
    prevent a user-installed `latexminted` executable from being accessible.

Requirements for locating and running a separate `latexminted` executable
under Windows:

  * The separate executable must be the first `latexminted.exe` found on PATH,
    or it must be the first `latexminted.exe` on PATH that is located under
    the user home directory.

  * The separate executable must be outside a TeX installation.  There is a
    check for a `tex.exe` executable in the same directory as
    `latexminted.exe`.  There is a check for the case-insensitive strings
    "texlive", "miktex", and "tinytex" in the path to the `latexminted`
    executable.  With TeX Live, the path to the `latexminted` executable is
    also compared to the environment variable `SELFAUTOLOC`.

  * The separate executable must be outside the current working directory,
    TEXMFOUTPUT, and TEXMF_OUTPUT_DIRECTORY.

  * The current directory, TEXMFOUTPUT, and TEXMF_OUTPUT_DIRECTORY cannot be
    subdirectories of the directory in which the executable is located.
'''


__version__ = '0.3.0'


import os
import pathlib
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




# Define function that determines whether subprocess executable paths are
# permitted.
prohibited_path_roots = set()
prohibited_path_roots.add(Path.cwd())
env_TEXMFOUTPUT = os.getenv('TEXMFOUTPUT')
env_TEXMF_OUTPUT_DIRECTORY = os.getenv('TEXMF_OUTPUT_DIRECTORY')
for env_var in (env_TEXMFOUTPUT, env_TEXMF_OUTPUT_DIRECTORY):
    if env_var:
        env_var_path = Path(env_var)
        prohibited_path_roots.add(env_var_path)
        prohibited_path_roots.add(env_var_path.resolve())

did_init_prohibited_path_roots = False
def is_permitted_executable_path(executable_path, executable_path_resolved):
    global did_init_prohibited_path_roots
    if not did_init_prohibited_path_roots:
        did_init_prohibited_path_roots = True
        init_prohibited_path_roots()
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
def init_prohibited_path_roots():
    if not env_TEXMFOUTPUT and env_SELFAUTOLOC and (not env_TEXSYSTEM or env_TEXSYSTEM.lower() != 'miktex'):
        if sys.platform == 'win32':
            # Under Windows, shell escape executables will often be launched
            # with the TeX Live `runscript.exe` executable wrapper.  This
            # overwrites `SELFAUTOLOC` from TeX with the location of the
            # wrapper, so `SELFAUTOLOC` may not be correct.
            which_tlmgr = shutil.which('tlmgr')  # No `.exe`; likely `.bat`
            if not which_tlmgr:
                sys.exit('Failed to find TeX Live "tlmgr" executable on PATH')
            which_tlmgr_resolved = Path(which_tlmgr).resolve()
            texlive_bin_path = which_tlmgr_resolved.parent
            # Make sure executable is *.exe, not *.bat or *.cmd:
            # https://docs.python.org/3/library/subprocess.html#security-considerations
            which_kpsewhich = shutil.which('kpsewhich.exe', path=str(texlive_bin_path))
            if not which_kpsewhich:
                sys.exit(
                    'Failed to find a TeX Live "tlmgr" executable with accompanying "kpsewhich" executable on PATH'
                )
            which_kpsewhich_path = Path(which_kpsewhich)
            which_kpsewhich_resolved = which_kpsewhich_path.resolve()
            if not texlive_bin_path == which_kpsewhich_resolved.parent:
                sys.exit(' '.join([
                    '"tlmgr" executable from PATH resolved to "{}" '.format(which_tlmgr_resolved.as_posix()),
                    'while "kpsewhich" resolved to "{}";'.format(which_kpsewhich_resolved.as_posix()),
                    '"tlmgr" and "kpsewhich" should be in the same location',
                ]))
            if not which_kpsewhich_resolved.name.lower().endswith('.exe'):
                sys.exit(' '.join([
                    'Executable "kpsewhich" resolved to "{}",'.format(which_kpsewhich_resolved.as_posix()),
                    'but *.exe is required',
                ]))
        else:
            which_kpsewhich = shutil.which('kpsewhich', path=env_SELFAUTOLOC)
            if not which_kpsewhich:
                sys.exit(' '.join([
                    'Environment variable SELFAUTOLOC has value "{}",'.format(env_SELFAUTOLOC),
                    'but a "kpsewhich" executable was not found at that location',
                ]))
            which_kpsewhich_path = Path(which_kpsewhich)
            which_kpsewhich_resolved = which_kpsewhich_path.resolve()
        if not is_permitted_executable_path(which_kpsewhich_path, which_kpsewhich_resolved):
            # As in the latexrestricted case, this doesn't initially check for
            # the TeX Live scenario where `TEXMFOUTPUT` is set in a
            # `texmf.cnf` config file to a location that includes the
            # `kpsewhich` executable.  There isn't a good way to get the value
            # of `TEXMFOUTPUT` without running `kpsewhich` in that case.
            sys.exit(
                'Executable "kpsewhich" is located under the current directory, TEXMFOUTPUT, or '
                'TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory as the executable'
            )
        kpsewhich_cmd = [which_kpsewhich_resolved.as_posix(), '--var-value', 'TEXMFOUTPUT']
        try:
            kpsewhich_proc = subprocess.run(kpsewhich_cmd, shell=False, capture_output=True)
        except PermissionError:
            sys.exit('Insufficient permission to run "{}"'.format(which_kpsewhich_resolved.as_posix()))
        kpsewhich_TEXMFOUTPUT = kpsewhich_proc.stdout.strip().decode(sys.stdout.encoding) or None
        if kpsewhich_TEXMFOUTPUT:
            kpsewhich_TEXMFOUTPUT_path = Path(kpsewhich_TEXMFOUTPUT)
            prohibited_path_roots.add(kpsewhich_TEXMFOUTPUT_path)
            prohibited_path_roots.add(kpsewhich_TEXMFOUTPUT_path.resolve())
        if not is_permitted_executable_path(which_kpsewhich_path, which_kpsewhich_resolved):
            # It is now possible to check for the TeX Live scenario where
            # `TEXMFOUTPUT` is set in a `texmf.cnf` config file to a location
            # that includes the `kpsewhich` executable.  Giving an error
            # message after already running `kpsewhich` isn't ideal, but there
            # isn't a good alternative.  As in the latexrestricted case, the
            # impact on overall security is negligible because an unsafe value
            # of `TEXMFOUTPUT` means that all TeX-related executables are
            # potentially compromised.
            sys.exit(
                'Executable "kpsewhich" is located under the current directory, TEXMFOUTPUT, or '
                'TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory as the executable'
            )




# If Python version is < 3.8, try to locate a more recent version and then
# relaunch this script with that Python version in a subprocess.
if sys.version_info[:2] < (3, 8):
    for minor_version in range(13, 7, -1):
        if sys.platform == 'win32':
            # Batch files must be prohibited:
            # https://docs.python.org/3/library/subprocess.html#security-considerations
            which_python = shutil.which('python3.{}.exe'.format(minor_version))
        else:
            which_python = shutil.which('python3.{}'.format(minor_version))
        if which_python:
            which_python_path = Path(which_python)
            which_python_resolved = which_python_path.resolve()
            if sys.platform == 'win32' and not which_python_resolved.name.lower().endswith('.exe'):
                continue
            if is_permitted_executable_path(which_python_path, which_python_resolved):
                python_cmd = [which_python_resolved.as_posix(), __file__] + sys.argv[1:]
                python_proc = subprocess.run(python_cmd, shell=False, capture_output=True)
                sys.stderr.buffer.write(python_proc.stderr)
                sys.stdout.buffer.write(python_proc.stdout)
                sys.exit(python_proc.returncode)
    sys.exit('latexminted requires Python >= 3.8, but a compatible Python executable was not found on PATH')




# Check for required wheel dependencies and add them to Python's `sys.path`.
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




# Under Windows, check PATH for a `latexminted` executable outside a TeX
# installation.  If a `latexminted` executable is found in a suitable location
# with sufficient precedence, run it in a subprocess and exit.
#
# The environment variable `LATEXMINTED_SUBPROCESS` is used to prevent an
# endless recursion of subprocesses in the event that a `latexminted`
# executable *inside* a TeX installation somehow manages to pass the tests for
# an executable *outside* a TeX installation.
if sys.platform == 'win32' and not os.getenv('LATEXMINTED_SUBPROCESS'):
    os.environ['LATEXMINTED_SUBPROCESS'] = '1'
    fallback_path_search = True
    if env_SELFAUTOLOC:
        env_SELFAUTOLOC_resolved = Path(env_SELFAUTOLOC).resolve()
    else:
        env_SELFAUTOLOC_resolved = None
    which_latexminted = shutil.which('latexminted.exe')
    if which_latexminted:
        which_latexminted_path = Path(which_latexminted)
        which_latexminted_resolved = which_latexminted_path.resolve()
        if not which_latexminted_resolved.name.lower().endswith('.exe'):
            sys.exit(' '.join([
                'Executable "latexminted" resolved to "{}",'.format(which_latexminted_resolved.as_posix()),
                'but *.exe is required',
            ]))
        if which_latexminted_resolved == script_resolved:
            pass
        elif (which_latexminted_resolved.parent / 'tex.exe').exists():
            pass
        elif any(x in which_latexminted_resolved.as_posix().lower() for x in ('texlive', 'miktex', 'tinytex')):
            pass
        elif env_SELFAUTOLOC_resolved and which_latexminted_resolved.is_relative_to(env_SELFAUTOLOC_resolved):
            pass
        elif is_permitted_executable_path(which_latexminted_path, which_latexminted_resolved):
            latexminted_cmd = [which_latexminted_resolved.as_posix()] + sys.argv[1:]
            latexminted_proc = subprocess.run(latexminted_cmd, shell=False, capture_output=True)
            sys.stderr.buffer.write(latexminted_proc.stderr)
            sys.stdout.buffer.write(latexminted_proc.stdout)
            sys.exit(latexminted_proc.returncode)
        else:
            # If there was a `latexminted` executable on PATH outside a TeX
            # installation, but it wasn't permitted due to its location, don't
            # perform fallback search.
            fallback_path_search = False
    if fallback_path_search:
        # Windows appends user PATH to system PATH, so the system PATH may
        # prevent finding a user installation of `latexminted`.  Search
        # through PATH elements under user home directory to check for
        # `latexminted.exe` outside a TeX installation.
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
            elif env_SELFAUTOLOC_resolved and which_latexminted_resolved.is_relative_to(env_SELFAUTOLOC_resolved):
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
