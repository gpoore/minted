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
from ._anypath import AnyPath
from ._latex_config import latex_config
from ._restricted_pathlib import RestrictedPath




_approved_executables = set([
    'kpsewhich',
    'initexmf',
])

_prohibited_path_roots: set[AnyPath] = set([AnyPath(latex_config.tex_cwd)])
for var in (latex_config.TEXMF_OUTPUT_DIRECTORY, latex_config.TEXMFOUTPUT):
    if var:
        var_path = AnyPath(var)
        _prohibited_path_roots.add(var_path)
        _prohibited_path_roots.add(var_path.resolve())




def restricted_run(args: list[str], allow_restricted_executables: bool = False) -> subprocess.CompletedProcess:
    '''
    Run a command securely, consistent with TeX restricted shell escape.

     *  By default, the executable must be in the list of approved executables
        in this file.  If `allow_restricted_executables == True`, then the
        executable must be in the list of allowed restricted shell escape
        commands as returned by `kpsewhich` or `initexmf`.

     *  The executable must be in the same directory as `kpsewhich` or
        `initexmf`, as previously located during LaTeX config evaluation, or
        the executable must exist on PATH, as found by `shutil.which()`.

        The executable must not be in a location writable by LaTeX.  For added
        security, locations writable by LaTeX cannot be under the executable
        parent directory.

     *  The executable cannot be a batch file (no *.bat or *.cmd):
        https://docs.python.org/3/library/subprocess.html#security-considerations.
        This is enforced in a somewhat redundant fashion by requiring *.exe
        under Windows and completely prohibiting *.bat and *.cmd everywhere.

     *  The subprocess must run with `shell=False`.
    '''

    if not isinstance(args, list) or not args or not all(isinstance(x, str) for x in args):
        raise TypeError
    if not isinstance(allow_restricted_executables, bool):
        raise TypeError

    executable = args[0]
    if executable not in _approved_executables:
        if not allow_restricted_executables or executable not in latex_config.restricted_shell_escape_commands:
            raise SubprocessUnapprovedExecutableError(f'Executable "{executable}" is not in the approved list')

    if latex_config.texlive_bin:
        which_executable = shutil.which(executable, path=latex_config.texlive_bin)
    elif latex_config.miktex_bin:
        which_executable = shutil.which(executable, path=latex_config.miktex_bin)
    else:
        raise TypeError
    if not which_executable:
        which_executable = shutil.which(executable)
    if not which_executable:
        raise SubprocessExecutableNotFoundError(f'Executable "{executable}" was not found')

    which_executable_path = RestrictedPath(which_executable)
    which_executable_resolved = which_executable_path.resolve()
    if platform.system() == 'Windows' and not which_executable_resolved.name.lower().endswith('.exe'):
        raise SubprocessUnapprovedExecutableError(
            f'Executable "{executable}" resolved to "{which_executable_path.as_posix()}", but *.exe is required'
        )
    if any(which_executable_path.name.lower().endswith(ext) for ext in ('.bat', '.cmd')):
        # This should be redundant
        raise SubprocessUnapprovedExecutableError(f'Executable "{executable}" not allowed (no *.bat or *.cmd)')

    if any(e.is_relative_to(p) or p.is_relative_to(e)
           for e in set([which_executable_path.parent, which_executable_resolved.parent])
           for p in _prohibited_path_roots):
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
