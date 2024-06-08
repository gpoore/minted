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

  * latex2pydata:  https://pypi.org/project/latex2pydata/

  * Pygments:  https://pypi.org/project/Pygments/

The combined executable plus wheels provide everything that is needed for the
Python side of the LaTeX minted package.  No additional Python libraries are
required.

The wheels require Python >= 3.8.  If this executable is launched with an
earlier Python version, then it will attempt to locate a more recent Python
installation and run itself with that Python version in a subprocess.  The
search for more recent Python versions looks for executables of the form
`python3.x`.

If the latexminted Python package is installed separately, then it will create
a `latexminted` executable as part of the installation process.  If that
executable exists and has higher precedence on PATH than this executable, then
that executable will run in a subprocess.  This makes it possible to install
latexminted, latex2pydata, and Pygments separately and then customize Pygments
with additional packages that provide plugins.

Conditions for running Python or a separate `latexminted` executable in a
subprocess:

  * The executable must exist on PATH, outside the current working directory
    or a subdirectory and outside TEXMFOUTPUT and TEXMF_OUTPUT_DIRECTORY.

  * The current directory, TEXMFOUTPUT, and TEXMF_OUTPUT_DIRECTORY cannot be
    subdirectories of the directory in which the executable is located.
'''


__version__ = '0.1.0b1'


import os
import pathlib
import platform
import shutil
import subprocess
import sys




# The `type(...)` is needed to inherit the `_flavour` attribute
class Path(type(pathlib.Path())):
    if sys.version_info[:2] < (3, 9):
        def is_relative_to(self, other):
            try:
                self.relative_to(other)
            except ValueError:
                return False
            return True

def is_permitted_executable_path(executable_path):
    prohibited_path_roots = [Path.cwd().resolve()]
    for variable in ('TEXMFOUTPUT', 'TEXMF_OUTPUT_DIRECTORY'):
        value = os.getenv(variable)
        if value:
            value_path = Path(value).resolve()
            prohibited_path_roots.append(value_path)
    if any(executable_path.is_relative_to(p) for p in prohibited_path_roots):
        return False
    if any(p.is_relative_to(executable_path) for p in prohibited_path_roots):
        return False
    return True




if sys.version_info[:2] < (3, 8):
    for minor_version in range(13, 7, -1):
        which_python = shutil.which('python3.{}'.format(minor_version))
        if which_python:
            if platform.system == 'Windows' and not which_python.lower().endswith('.exe'):
                # Batch files must be prohibited:
                # https://docs.python.org/3/library/subprocess.html#security-considerations
                continue
            which_python_resolved = Path(which_python).resolve()
            if is_permitted_executable_path(which_python_resolved):
                cmd = [which_python_resolved.as_posix(), __file__] + sys.argv[1:]
                proc = subprocess.run(cmd, shell=False, capture_output=True)
                sys.stderr.buffer.write(proc.stderr)
                sys.stdout.buffer.write(proc.stdout)
                sys.exit(proc.returncode)
    sys.exit('latexminted requires Python >= 3.8, but a compatible Python executable was not found on PATH')


script_resolved = Path(__file__).resolve()


for which_latexminted in [shutil.which('latexminted'), shutil.which('latexminted', path=str(Path.home()))]:
    if which_latexminted:
        which_latexminted_resolved = Path(which_latexminted).resolve()
        if (is_permitted_executable_path(which_latexminted_resolved) and
                script_resolved != which_latexminted_resolved and
                (platform.system != 'Windows' or not (which_latexminted_resolved.parent / 'tex.exe').exists()) and
                not any(x in which_latexminted_resolved.as_posix().lower() for x in ('texlive', 'miktex', 'tinytex'))):
            cmd = [which_latexminted_resolved] + sys.argv[1:]
            proc = subprocess.run(cmd, shell=False, capture_output=True)
            sys.stderr.buffer.write(proc.stderr)
            sys.stdout.buffer.write(proc.stdout)
            sys.exit(proc.returncode)


required_wheel_packages = ('latexminted', 'latex2pydata', 'pygments')
wheel_paths = [p for p in script_resolved.parent.glob('*.whl') if p.name.startswith(required_wheel_packages)]
if not wheel_paths:
    sys.exit('latexminted failed to find bundled wheels *.whl')
for pkg in required_wheel_packages:
    if not any(whl.name.startswith(pkg) for whl in wheel_paths):
        sys.exit('latexminted failed to find all required bundled wheels *.whl')
for wheel_path in wheel_paths:
    sys.path.insert(0, wheel_path.as_posix())
from latexminted.cmdline import main
main()
