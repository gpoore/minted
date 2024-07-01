# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from ..err import LatexConfigError
from ._anypath import AnyPath




class LatexConfig(object):
    '''
    Access config settings from `kpsewhich` (TeX Live) or `initexmf` (MiKTeX),
    plus related environment variables.  Also locate files via `kpsewhich`.

    With TeX Live, the environment variable SELFAUTOLOC is used to determine
    the correct `kpsewhich` executable on systems with multiple TeX
    installations.  With MiKTeX, Python's `shutil.which()` is used to locate
    `initexmf`, and then the location of `initexmf` is used to find the
    accompanying `kpsewhich` (unless SELFAUTOLOC has been set manually).

    File read/write permission settings are available via the following
    properties:

      * `can_read_dotfiles`
      * `can_read_anywhere`
      * `can_write_dotfiles`
      * `can_write_anywhere`

    The `*dotfile` settings determine whether files with names starting with a
    dot `.` are allowed to be read/written.  The `*anywhere` settings
    determine whether files anywhere are allowed to be read/written, or only
    files within the current working directory, $TEXMFOUTPUT,
    $TEXMF_OUTPUT_DIRECTORY, and their subdirectories.  The values of these
    properties are determined from `openout_any` and `openin_any` settings in
    `texmf.cnf` for TeX Live, and from `[Core]AllowUnsafeInputFiles` and
    `[Core]AllowUnsafeOutputFiles` in `miktex.ini` for MiKTeX.

    Python properties and caching are used extensively so that `kpsewhich` and
    `initexmf` subprocesses only run when their output is actually used and
    has not been obtained previously.
    '''

    def __init__(self):
        pass


    _permitted_subprocess_executables = set(['kpsewhich', 'initexmf'])
    _permitted_subprocess_executables.update([f'{executable}.exe' for executable in _permitted_subprocess_executables])

    _tex_cwd = AnyPath.cwd()
    tex_cwd = str(_tex_cwd)

    _prohibited_subprocess_executable_roots: set[AnyPath] = set()
    _prohibited_subprocess_executable_roots.add(_tex_cwd)
    for env_var in [os.getenv(x) for x in ('TEXMFOUTPUT', 'TEXMF_OUTPUT_DIRECTORY')]:
        if env_var:
            _prohibited_subprocess_executable_roots.add(AnyPath(env_var))
    _prohibited_subprocess_executable_roots.update([p.resolve() for p in _prohibited_subprocess_executable_roots])

    @classmethod
    def _resolve_and_check_executable(cls, executable_name: str, executable_path: AnyPath) -> AnyPath:
        executable_resolved = executable_path.resolve()
        # There is no check for `executable_path.name`, because
        # `executable_path` is always from `shutil.which(<name>)`.
        if executable_resolved.name not in cls._permitted_subprocess_executables:
            raise LatexConfigError(
                f'Executable "{executable_name}" resolved to "{executable_resolved}", '
                f'but "{executable_resolved.name}" is not one of the permitted executables '
                'for determining LaTeX configuration'
            )
        # Executable path can't be writable by LaTeX.  LaTeX writable path(s)
        # can't be relative to the executable's parent directory, since that
        # could make some of the executable's resources writable.  Path
        # comparisons are performed with all permutations of resolved and
        # unresolved paths to reduce the potential for symlink trickery.
        #
        # Fully eliminating the potential for symlink trickery would require
        # checking all locations writable by LaTeX for symlinks to problematic
        # locations.  That isn't worth doing since TeX path security does not
        # consider symlinks.
        if any(e.is_relative_to(p) or p.is_relative_to(e)
               for e in set([executable_path.parent, executable_resolved.parent])
               for p in cls._prohibited_subprocess_executable_roots):
            # This doesn't check for the scenario where `TEXMFOUTPUT` is
            # set in a `texmf.cnf` config file.  There isn't a good way to
            # check for that without `kpsewhich`.
            raise LatexConfigError(
                f'Executable "{executable_name}" is located under the current directory, $TEXMFOUTPUT, or '
                '$TEXMF_OUTPUT_DIRECTORY, or one of these locations is under the same directory as the executable'
            )
        return executable_resolved


    _did_init_tex_paths: bool = False
    _texlive_bin: str | None = None
    _texlive_kpsewhich: str | None = None
    _miktex_bin: str | None
    _miktex_initexmf: str | None = None
    _miktex_kpsewhich: str | None = None

    @classmethod
    def _init_tex_paths(cls):
        SELFAUTOLOC = os.getenv('SELFAUTOLOC')
        TEXSYSTEM = os.getenv('TEXSYSTEM')
        if SELFAUTOLOC:
            if platform.system() == 'Windows':
                # Make sure executable is *.exe, not *.bat or *.cmd:
                # https://docs.python.org/3/library/subprocess.html#security-considerations
                which_kpsewhich = shutil.which('kpsewhich.exe', path=SELFAUTOLOC)
            else:
                which_kpsewhich = shutil.which('kpsewhich', path=SELFAUTOLOC)
            if which_kpsewhich:
                which_kpsewhich_path = AnyPath(which_kpsewhich)
                which_kpsewhich_resolved = cls._resolve_and_check_executable('kpsewhich', which_kpsewhich_path)
                if TEXSYSTEM and TEXSYSTEM.lower() == 'miktex':
                    if platform.system() == 'Windows':
                        which_initexmf = shutil.which('initexmf.exe', path=SELFAUTOLOC)
                    else:
                        which_initexmf = shutil.which('initexmf', path=SELFAUTOLOC)
                    if not which_initexmf:
                        raise LatexConfigError(
                            f'Environment variable TEXSYSTEM has value "{TEXSYSTEM}" and '
                            f'environment variable SELFAUTOLOC has value "{SELFAUTOLOC}", '
                            'but a MiKTeX "initexmf" executable was not found at that location'
                        )
                    which_initexmf_path = AnyPath(which_initexmf)
                    which_initexmf_resolved = cls._resolve_and_check_executable('initexmf', which_initexmf_path)
                    cls._miktex_bin = str(which_initexmf_path.parent)
                    cls._miktex_initexmf = str(which_initexmf_resolved)
                    cls._miktex_kpsewhich = str(which_kpsewhich_resolved)
                else:
                    cls._texlive_bin = str(which_kpsewhich_path.parent)
                    cls._texlive_kpsewhich = str(which_kpsewhich_resolved)
                cls._did_init_tex_paths = True
                return
            raise LatexConfigError(
                f'Environment variable SELFAUTOLOC has value "{SELFAUTOLOC}", '
                'but a "kpsewhich" executable was not found at that location'
            )
        if TEXSYSTEM and TEXSYSTEM.lower() == 'miktex':
            # Unlike the TeX Live case, there isn't a good way deal with the
            # possibility of multiple installations, so just use
            # `shutil.which()` without a specified `path`.
            if platform.system() == 'Windows':
                which_initexmf = shutil.which('initexmf.exe')
            else:
                which_initexmf = shutil.which('initexmf')
            if which_initexmf:
                which_initexmf_path = AnyPath(which_initexmf)
                which_initexmf_resolved = cls._resolve_and_check_executable('initexmf', which_initexmf_path)
                if platform.system() == 'Windows':
                    which_kpsewhich = shutil.which('kpsewhich.exe', path=str(which_initexmf_resolved.parent))
                else:
                    which_kpsewhich = shutil.which('kpsewhich', path=str(which_initexmf_resolved.parent))
                if which_kpsewhich:
                    which_kpsewhich_path = AnyPath(which_kpsewhich)
                    which_kpsewhich_resolved = cls._resolve_and_check_executable('kpsewhich', which_kpsewhich_path)
                    cls._miktex_bin = str(which_initexmf_path.parent)
                    cls._miktex_initexmf = str(which_initexmf_resolved)
                    cls._miktex_kpsewhich = str(which_kpsewhich_resolved)
                    cls._did_init_tex_paths = True
                    return
            raise LatexConfigError(
                f'Environment variable TEXSYSTEM has value "{TEXSYSTEM}", '
                'but a MiKTeX "initexmf" executable with accompanying "kpsewhich" was not found on PATH'
            )
        raise LatexConfigError(
            'Expected environment variables SELFAUTOLOC and/or TEXSYSTEM were not found or had invalid values, '
            'so "kpsewhich" executable and/or MiKTeX "initexmf" executable could not be found'
        )

    # Locations of TeX executables must be returned as strings, not as
    # `AnyPath`.  All non-private paths should be subclasses of
    # `RestrictedPath`, but it can't be defined without `LatexConfig`.

    @property
    def texlive_bin(self) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        return self._texlive_bin

    @property
    def texlive_kpsewhich(self) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        return self._texlive_kpsewhich

    @property
    def miktex_bin(self) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        return self._miktex_bin

    @property
    def miktex_initexmf(self) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        return self._miktex_initexmf

    @property
    def miktex_kpsewhich(self) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        return self._miktex_kpsewhich


    def kpsewhich_find_config_file(self, file: str,) -> str | None:
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        if self.texlive_kpsewhich:
            kpsewhich = self.texlive_kpsewhich
        elif self.miktex_kpsewhich:
            kpsewhich = self.miktex_kpsewhich
        else:
            raise TypeError
        cmd = [kpsewhich, '-f', 'othertext', file]
        proc = subprocess.run(cmd, shell=False, capture_output=True)
        value = proc.stdout.strip().decode(sys.stdout.encoding) or None
        return value

    _kpsewhich_find_file_cache: dict[str, str | None] = {}

    def kpsewhich_find_file(self, file: str, *, cache: bool = False) -> str | None:
        if cache:
            try:
                return self._kpsewhich_find_file_cache[file]
            except KeyError:
                pass
        if not self._did_init_tex_paths:
            self._init_tex_paths()
        if self.texlive_kpsewhich:
            kpsewhich = self.texlive_kpsewhich
        elif self.miktex_kpsewhich:
            kpsewhich = self.miktex_kpsewhich
        else:
            raise TypeError
        cmd = [kpsewhich, file]
        proc = subprocess.run(cmd, shell=False, capture_output=True)
        value = proc.stdout.strip().decode(sys.stdout.encoding) or None
        if cache:
            self._kpsewhich_find_file_cache[file] = value
        return value


    _texlive_var_value_cache: dict[str, str | None] = {}

    @classmethod
    def _get_texlive_var_value(cls, var: str) -> str | None:
        try:
            return cls._texlive_var_value_cache[var]
        except KeyError:
            pass
        if cls._texlive_kpsewhich is None:
            raise TypeError
        cmd = [cls._texlive_kpsewhich, '--var-value', var]
        proc = subprocess.run(cmd, shell=False, capture_output=True)
        value = proc.stdout.strip().decode(sys.stdout.encoding) or None
        if var.lower() in ('openin_any', 'openout_any'):
            # Documentation for `openin_any` and `openout_any` values:
            # https://www.tug.org/texinfohtml/kpathsea.html#Safe-filenames-1
            if value:
                value = value.lower()
            if value in ('y', '1'):
                value = 'a'
            elif value in ('n', '0'):
                value = 'r'
            elif value not in ('a', 'r', 'p'):
                value = 'p'
        elif var.lower() == 'shell_escape_commands':
            if value:
                value = value.rstrip(',%')
        cls._texlive_var_value_cache[var] = value
        return value

    _miktex_config_value_cache: dict[str, str | None] = {}

    @classmethod
    def _get_miktex_config_value(cls, var: str) -> str | None:
        try:
            return cls._miktex_config_value_cache[var]
        except KeyError:
            pass
        if cls._miktex_initexmf is None:
            raise TypeError
        cmd = [cls._miktex_initexmf, '--show-config-value', var]
        proc = subprocess.run(cmd, shell=False, capture_output=True)
        value = proc.stdout.strip().decode(sys.stdout.encoding) or None
        if var.lower() in ('[core]allowunsafeinputfiles', '[core]allowunsafeoutputfiles'):
            if value not in ('true', 'false'):
                value = 'false'
        cls._miktex_config_value_cache[var] = value
        return value


    _did_init_read_settings: bool = False
    _can_read_dotfiles: bool = False
    _can_read_anywhere: bool = False

    _did_init_write_settings: bool = False
    _can_write_dotfiles: bool = False
    _can_write_anywhere: bool = False

    # Documentation for `openin_any` and `openout_any` values:
    # https://www.tug.org/texinfohtml/kpathsea.html#Safe-filenames-1

    @classmethod
    def _init_read_settings(cls):
        if not cls._did_init_tex_paths:
            cls._init_tex_paths()
        if cls._texlive_kpsewhich:
            openin_any = cls._get_texlive_var_value('openin_any')
            if openin_any == 'a':
                cls._can_read_dotfiles = True
                cls._can_read_anywhere = True
            elif openin_any == 'r':
                cls._can_read_dotfiles = False
                cls._can_read_anywhere = True
            elif openin_any == 'p':
                cls._can_read_dotfiles = False
                cls._can_read_anywhere = False
            else:
                raise ValueError
        elif cls._miktex_initexmf:
            allow_unsafe_input_files = cls._get_miktex_config_value('[Core]AllowUnsafeInputFiles')
            if allow_unsafe_input_files == 'true':
                cls._can_read_dotfiles = True
                cls._can_read_anywhere = True
            elif allow_unsafe_input_files == 'false':
                cls._can_read_dotfiles = False
                cls._can_read_anywhere = False
            else:
                raise ValueError
        else:
            raise TypeError
        cls._did_init_read_settings = True

    @property
    def can_read_dotfiles(self) -> bool:
        if not self._did_init_read_settings:
            self._init_read_settings()
        return self._can_read_dotfiles

    @property
    def can_read_anywhere(self) -> bool:
        if not self._did_init_read_settings:
            self._init_read_settings()
        return self._can_read_anywhere

    @classmethod
    def _init_write_settings(cls):
        if not cls._did_init_tex_paths:
            cls._init_tex_paths()
        if cls._texlive_kpsewhich:
            openout_any = cls._get_texlive_var_value('openout_any')
            if openout_any == 'a':
                cls._can_write_dotfiles = True
                cls._can_write_anywhere = True
            elif openout_any == 'r':
                cls._can_write_dotfiles = False
                cls._can_write_anywhere = True
            elif openout_any == 'p':
                cls._can_write_dotfiles = False
                cls._can_write_anywhere = False
            else:
                raise ValueError
        elif cls._miktex_initexmf:
            allow_unsafe_output_files = cls._get_miktex_config_value('[Core]AllowUnsafeOutputFiles')
            if allow_unsafe_output_files is True:
                cls._can_write_dotfiles = True
                cls._can_write_anywhere = True
            elif allow_unsafe_output_files is False:
                cls._can_write_dotfiles = False
                cls._can_write_anywhere = False
            else:
                raise TypeError
        else:
            raise TypeError
        cls._did_init_write_settings = True

    @property
    def can_write_dotfiles(self) -> bool:
        if not self._did_init_write_settings:
            self._init_write_settings()
        return self._can_write_dotfiles

    @property
    def can_write_anywhere(self) -> bool:
        if not self._did_init_write_settings:
            self._init_write_settings()
        return self._can_write_anywhere

    _prohibited_write_file_extensions: set[str]
    if platform.system() == 'Windows':
        # Fallback value:
        # https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start
        _prohibited_write_file_extensions = set(
            (os.getenv('PATHEXT') or '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC').lower().split(os.pathsep)
        )
    else:
        _prohibited_write_file_extensions = set()

    @property
    def prohibited_write_file_extensions(self) -> set[str]:
        return self._prohibited_write_file_extensions


    _var_cache: dict[str, str | None] = {}

    @property
    def TEXMFHOME(self) -> str | None:
        try:
            value = self._var_cache['TEXMFHOME']
        except KeyError:
            if self.texlive_kpsewhich:
                value = self._get_texlive_var_value('TEXMFHOME')
            elif self.miktex_initexmf:
                value = self._get_miktex_config_value('TEXMFHOME')
            else:
                raise TypeError
            self._var_cache['TEXMFHOME'] = value
        return value

    @property
    def TEXMFOUTPUT(self) -> str | None:
        try:
            value = self._var_cache['TEXMFOUTPUT']
        except KeyError:
            value = os.getenv('TEXMFOUTPUT')
            if value is None and self.texlive_kpsewhich:
                # TeX Live allows `TEXMFOUTPUT` to be set in `texmf.cnf`
                value = self._get_texlive_var_value('TEXMFOUTPUT')
            self._var_cache['TEXMFOUTPUT'] = value
        return value

    @property
    def TEXMF_OUTPUT_DIRECTORY(self) -> str | None:
        try:
            value = self._var_cache['TEXMF_OUTPUT_DIRECTORY']
        except KeyError:
            value = os.getenv('TEXMF_OUTPUT_DIRECTORY')
            self._var_cache['TEXMF_OUTPUT_DIRECTORY'] = value
        return value

    @property
    def restricted_shell_escape_commands(self) -> set[str]:
        commands = set()
        if self.texlive_kpsewhich:
            value = self._get_texlive_var_value('shell_escape_commands')
            if value is not None:
                commands.update(value.split(','))
            return commands
        if self.miktex_initexmf:
            value = self._get_miktex_config_value('[Core]AllowedShellCommands[]')
            if value is not None:
                commands.update(value.split(';'))
            return commands
        raise TypeError




latex_config = LatexConfig()
