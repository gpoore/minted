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
This Python executable is intended for installation within a TeX distribution.
It provides access to the `latexminted` library in a manner that is
compatible with restricted shell escape security requirements under Windows.

If the necessary libraries are available, run `latexminted.cmdline.main()`.

Otherwise, attempt to locate `latexminted.exe` and run it via `subprocess`.
Conditions for running `latexminted.exe`:

  * It must exist on PATH, outside the current working directory or a
    subdirectory and outside $TEXMFOUTPUT and $TEXMF_OUTPUT_DIRECTORY.

  * It must be within a directory structure that looks like this:
    ```
    <py_dir>/python.exe
    <py_dir>/Scripts/latexminted.exe
    ```
    The `python.exe` must be executable and on PATH.

  * The current directory, $TEXMFOUTPUT, and $TEXMF_OUTPUT_DIRECTORY cannot be
    subdirectories of the directory in which `python.exe` is located.
'''


from __future__ import annotations


__version__ = '0.1.0b1'


import sys
try:
    from latexminted.cmdline import main
except ImportError:
    pass
else:
    main(latexmintedwin=__version__)
    sys.exit()


import os
import pathlib
import shutil
import subprocess
import sys
# Set environment variable `NoDefaultCurrentDirectoryInExePath` to exclude
# current directory for Python 3.12+.
#
# Compare
#  *  https://docs.python.org/3.12/library/shutil.html#shutil.which
# versus
#  *  https://docs.python.org/3.11/library/shutil.html#shutil.which
os.environ['NoDefaultCurrentDirectoryInExePath'] = '1'
which_latexminted = shutil.which('latexminted.exe')
if not which_latexminted:
    sys.exit(
        'The default Python interpreter does not have the latexminted library installed, '
        'and the latexminted executable cannot be found on PATH'
    )
# For Python < 3.12, make sure that `latexminted.exe` isn't in the current
# directory.  For all Python versions, make sure that it isn't in another
# problematic location.  Using `.resolve()` may not be strictly necessary, but
# ensures that there is no symlink trickery.
which_latexminted_path = pathlib.Path(which_latexminted).resolve()
if not which_latexminted_path.name.lower().endswith('.exe'):
    # This shouldn't happen, but batch files must be prohibited:
    # https://docs.python.org/3/library/subprocess.html#security-considerations
    sys.exit('Failed to find latexminted.exe')
prohibited_path_roots = [pathlib.Path.cwd().resolve()]
for variable in ('TEXMFOUTPUT', 'TEXMF_OUTPUT_DIRECTORY'):
    value = os.getenv(variable)
    if value:
        value_path = pathlib.Path(value).resolve()
        prohibited_path_roots.append(value_path)
if any(which_latexminted_path.is_relative_to(p) for p in prohibited_path_roots):
    sys.exit(
        'Cannot run latexminted executable located under the current directory, $TEXMFOUTPUT, or $TEXMF_OUTPUT_DIRECTORY: '
        f'"{which_latexminted_path}"'
    )
if which_latexminted_path.parent.name != 'Scripts':
    sys.exit(
        'Cannot run latexminted executable that was expected in Python "Scripts/" directory but found in '
        f'"{which_latexminted_path.parent.name}/"'
    )
which_python_for_latexminted = shutil.which('python.exe', path=which_latexminted_path.parent.parent)
if not which_python_for_latexminted:
    sys.exit(
        'Cannot run latexminted executable in directory that does not have "python.exe" one level up: '
        f'"{which_latexminted_path}"'
    )
which_python_for_latexminted_path = pathlib.Path(which_python_for_latexminted).resolve()
if which_python_for_latexminted_path.parent != which_latexminted_path.parent.parent:
    # Guard against resolving to unexpected location
    sys.exit(
        'Cannot run latexminted executable in directory that does not have "python.exe" one level up: '
        f'"{which_latexminted_path}"'
    )
if not which_python_for_latexminted_path.name.lower().endswith('.exe'):
    # This shouldn't happen, but batch files must be prohibited:
    # https://docs.python.org/3/library/subprocess.html#security-considerations
    sys.exit(
        'Cannot run latexminted executable in directory that does not have "python.exe" one level up: '
        f'"{which_latexminted_path}"'
    )
if any(p.is_relative_to(which_python_for_latexminted_path.parent) for p in prohibited_path_roots):
    sys.exit(
        'Cannot run latexminted executable when the current directory, $TEXMFOUTPUT, or $TEXMF_OUTPUT_DIRECTORY is within a Python installation: '
        f'"{which_python_for_latexminted_path.parent}"'
    )
# Use resolved executable path for subprocess.  Using just the executable
# name should give the same results, but this guards against any mismatch
# between how Python resolves the executable name with no path versus how
# the subprocess would resolve it.
latexminted_proc = subprocess.run([which_latexminted_path.as_posix()] + sys.argv[1:], shell=False, capture_output=True)
sys.stderr.buffer.write(latexminted_proc.stderr)
sys.stdout.buffer.write(latexminted_proc.stdout)
sys.exit(latexminted_proc.returncode)
