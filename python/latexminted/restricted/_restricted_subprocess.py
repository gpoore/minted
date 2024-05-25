# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import platform
import shutil
import subprocess
from ..err import SubprocessUnapprovedExecutableError, SubprocessExecutableNotFoundError, SubprocessExecutablePathSecurityError
from ._restricted_pathlib import RestrictedPath




approved_executables = set([
    'kpsewhich',
])




def restricted_run(args: list[str]) -> subprocess.CompletedProcess:
    '''
    Run a command securely, consistent with TeX restricted shell escape.

     *  The executable must be in the list of approved executables in this
        file.

     *  The executable must exist on PATH, as found by `shutil.which()`.  It
        must not be in a location writable by LaTeX.  For added security,
        locations writable by LaTeX cannot be under the executable parent
        directory.  Location is checked via `.is_executable_file_location()`
        from `_restricted_pathlib`.

     *  The executable cannot be a batch file (no *.bat or *.cmd):
        https://docs.python.org/3/library/subprocess.html#security-considerations.
        This is enforced in a somewhat redundant fashion by requiring *.exe
        under Windows and completely prohibiting *.bat and *.cmd everywhere.

     *  The subprocess must run with `shell=False`.
    '''

    if not isinstance(args, list) or not args or not all(isinstance(x, str) for x in args):
        raise TypeError

    executable = args[0]
    if executable not in approved_executables:
        raise SubprocessUnapprovedExecutableError(f'Executable "{executable}" is not in the approved list')

    which_executable = shutil.which(executable)
    if not which_executable:
        raise SubprocessExecutableNotFoundError(f'Executable "{executable}" was not found')

    which_executable_path = RestrictedPath(which_executable).resolve()
    if platform.system() == 'Windows' and not which_executable_path.name.lower().endswith('.exe'):
        raise SubprocessUnapprovedExecutableError(
            f'Executable "{executable}" resolved to "{which_executable_path.as_posix()}", but *.exe is required'
        )
    if any(which_executable_path.name.lower().endswith(ext) for ext in ('.bat', '.cmd')):
        # This should be redundant
        raise SubprocessUnapprovedExecutableError(f'Executable "{executable}" not allowed (no *.bat or *.cmd)')
    if not which_executable_path.is_executable_file_location():
        raise SubprocessExecutablePathSecurityError(
            f'Executable "{executable}" is located under the current directory, $TEXMFOUTPUT, '
            'or $TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory '
            'as the executable'
        )

    # Use resolved executable path for subprocess.  Using just the executable
    # name should give the same results, but this guards against any mismatch
    # between how Python resolves the executable name with no path versus how
    # the subprocess would resolve it.
    resolved_args = [which_executable_path.as_posix()] + args[1:]
    proc = subprocess.run(resolved_args, shell=False, capture_output=True)
    return proc
