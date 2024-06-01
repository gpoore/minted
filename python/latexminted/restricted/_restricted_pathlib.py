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
import pathlib
import re
from ..err import PathSecurityError




# The `type(...)` is needed to inherit the `_flavour` attribute
class RestrictedPath(type(pathlib.Path())):
    '''
    Subclass of `pathlib.Path` (which is system-dependent) that restricts file
    operations to be consistent with TeX restricted shell escape security
    requirements.  For this to be effective, all file operations must go
    through this class; it must not be bypassed with other modules such as
    `os` and `shutil` or functions such as `open()`.

     *  Reading:  Restricted to `.read_text()`, `.read_bytes()`, and
        `.open()`.

     *  Writing:  Restricted to `.write_text()` and `.open()`.  Restricted to
        files under the current working directory, $TEXMFOUTPUT, and
        $TEXMF_OUTPUT_DIRECTORY that have names matching the regular
        expression for minted temp files or cache files.

     *  Deleting files:  Restricted to `.unlink()`.  Restricted to files under
        the current working directory, $TEXMFOUTPUT, and
        $TEXMF_OUTPUT_DIRECTORY that have names matching the regular
        expression for minted temp files or cache files.

     *  Creating directories:  Restricted to `.mkdir()`.  Restricted to
        directories under the current working directory, $TEXMFOUTPUT, and
        $TEXMF_OUTPUT_DIRECTORY.

     *  Deleting directories:  Restricted to `.rmdir()`.  Restricted to
        directories under the current working directory, $TEXMFOUTPUT, and
        $TEXMF_OUTPUT_DIRECTORY.  `super().rmdir()` requires an empty
        directory, so no additional checks are needed to ensure that only
        permitted files are deleted.

     *  Completely prohibited:
         -  `.chmod()`
         -  `.lchmod()`
         -  `.write_bytes()` (use `.write_text()`)
         -  `.rename()`
         -  `.replace()`
         -  `.symlink_to()`
         -  `.hardlink_to()`
         -  `.touch()`
    '''

    # `super().resolve()` is used frequently in determining whether paths are
    # readable/writable/executable.  `.resolve()` and `.parent()` cache and
    # track resolved paths to minimize file system access.
    _resolved_set: set[RestrictedPath] = set()
    _resolve_cache: dict[RestrictedPath, RestrictedPath] = {}

    def resolve(self) -> RestrictedPath:
        try:
            resolved = self._resolve_cache[self]
        except KeyError:
            resolved = super().resolve()
            self._resolved_set.add(resolved)
            self._resolve_cache[self] = resolved
            self._resolve_cache[resolved] = resolved
        return resolved

    @property
    def parent(self) -> RestrictedPath:
        parent = super().parent
        if self in self._resolved_set:
            self._resolved_set.add(parent)
            self._resolve_cache[parent] = parent
        return parent

    # There are currently no restrictions on reading locations, but the
    # implementation allows this to be added.  This is equivalent to
    # TeX Live's `openin_any = a`; see
    # https://tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/texmf.cnf?revision=70942&view=markup#l634.
    _fs_read_roots: set[pathlib.Path] = set()
    # Similarly, there are no restrictions on reading dotfiles, but the
    # implementation allows this to be added.
    _fs_read_dotfiles: bool = True

    _fs_write_roots: set[pathlib.Path] = set()
    _fs_write_roots.add(pathlib.Path.cwd().resolve())
    for variable in ('TEXMFOUTPUT', 'TEXMF_OUTPUT_DIRECTORY'):
        value = os.getenv(variable)
        if value:
            value_path = pathlib.Path(value).resolve()
            _fs_write_roots.add(value_path)

    # Track readable/writable directories and files separately, since some of
    # the requirements are different.

    _checked_readable_dir_set: set[RestrictedPath] = set()
    _is_readable_dir_set: set[RestrictedPath] = set()

    _checked_readable_file_set: set[RestrictedPath] = set()
    _is_readable_file_set: set[RestrictedPath] = set()

    _checked_writable_dir_set: set[RestrictedPath] = set()
    _is_writable_dir_set: set[RestrictedPath] = set()

    _checked_writable_file_set: set[RestrictedPath] = set()
    _is_writable_file_set: set[RestrictedPath] = set()

    # `[0-9a-zA-Z_-]+` covers temp file names `_<MD5 hash>` plus code cache
    # file names `<MD5 hash>` plus style names `<style name>`.
    _writable_filename_re = re.compile(r'[0-9a-zA-Z_-]+\.(?:config|data|errlog|highlight|index|message|style)\.minted')

    _checked_executable_file_location_set: set[RestrictedPath] = set()
    _is_executable_file_location_set: set[RestrictedPath] = set()

    def is_readable_dir(self) -> bool:
        if self not in self._checked_readable_dir_set:
            resolved = self.resolve()
            if not self._fs_read_roots or any(resolved.is_relative_to(p) for p in self._fs_read_roots):
                self._is_readable_dir_set.add(self)
            self._checked_readable_dir_set.add(self)
        return self in self._is_readable_dir_set

    def is_readable_file(self) -> bool:
        if self not in self._checked_readable_file_set:
            resolved = self.resolve()
            if (resolved.parent.is_readable_dir() and (self._fs_read_dotfiles or not resolved.name.startswith('.'))):
                self._is_readable_file_set.add(self)
            self._checked_readable_file_set.add(self)
        return self in self._is_readable_file_set

    def is_writable_dir(self) -> bool:
        if self not in self._checked_writable_dir_set:
            resolved = self.resolve()
            if any(resolved.is_relative_to(p) for p in self._fs_write_roots):
                self._is_writable_dir_set.add(self)
            self._checked_writable_dir_set.add(self)
        return self in self._is_writable_dir_set

    def is_writable_file(self) -> bool:
        if self not in self._checked_writable_file_set:
            resolved = self.resolve()
            if (resolved.parent.is_writable_dir() and self._writable_filename_re.fullmatch(resolved.name)):
                self._is_writable_file_set.add(self)
            self._checked_writable_file_set.add(self)
        return self in self._is_writable_file_set

    def is_executable_file_location(self) -> bool:
        '''
        Note that this only checks whether the path is outside prohibited or
        problematic locations, hence the `_location`.  It does NOT check
        whether the file is executable or is on PATH.  For correct results,
        the executable should be located with `shutil.which()`, and then the
        path derived from this should be checked with
        `.is_executable_file_location()`.  See
        `restricted_subprocess.restricted_run()`.
        '''
        if self not in self._checked_executable_file_location_set:
            resolved = self.resolve()
            parent = resolved.parent
            if (not any(resolved.is_relative_to(p) for p in self._fs_write_roots) and
                    not any(p.is_relative_to(parent) for p in self._fs_write_roots)):
                self._is_executable_file_location_set.add(self)
            self._checked_executable_file_location_set.add(self)
        return self in self._is_executable_file_location_set


    def chmod(self, *args, **kwargs):
        raise NotImplementedError

    def lchmod(self, *args, **kwargs):
        raise NotImplementedError

    def mkdir(self, *args, **kwargs):
        if not self.is_writable_dir():
            raise PathSecurityError(
                f'Cannot create directory because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().mkdir(*args, **kwargs)

    def open(self, mode: str, **kwargs):
        # This check is redundant for the `.read_text()`, `.write_text()`,
        # etc. cases which call `.open()` internally.  However, checks on all
        # methods are needed for completeness, and also to guard against the
        # possibility of future implementation changes in `pathlib`.
        if mode in ('r', 'rb'):
            if not self.is_readable_file():
                raise PathSecurityError(
                    f'Cannot read file because it is outside permitted locations:  "{self.as_posix()}"'
                )
        elif mode in ('w', 'wb'):
            if not self.is_writable_file():
                raise PathSecurityError(
                    f'Cannot write file because it is outside permitted locations:  "{self.as_posix()}"'
                )
        else:
            raise NotImplementedError
        return super().open(mode=mode, **kwargs)

    def read_bytes(self, *args, **kwargs):
        if not self.is_readable_file():
            raise PathSecurityError(
                f'Cannot read file because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().read_bytes(*args, **kwargs)

    def read_text(self, encoding='utf-8-sig', errors='strict') -> str:
        if not self.is_readable_file():
            raise PathSecurityError(
                f'Cannot read file because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().read_text(encoding=encoding, errors=errors)

    def rename(self, *args, **kwargs):
        raise NotImplementedError

    def replace(self, *args, **kwargs):
        raise NotImplementedError

    def rmdir(self):
        if not self.is_writable_dir():
            raise PathSecurityError(
                f'Cannot delete directory because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().rmdir()

    def symlink_to(self, *args, **kwargs):
        raise NotImplementedError

    def hardlink_to(self, *args, **kwargs):
        raise NotImplementedError

    def touch(self, *args, **kwargs):
        raise NotImplementedError

    def unlink(self, missing_ok: bool = False):
        if not self.is_writable_file():
            raise PathSecurityError(
                f'Cannot delete file because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().unlink(missing_ok=missing_ok)

    def write_bytes(self, *args, **kwargs):
        raise NotImplementedError

    def write_text(self, data: str, encoding: str = 'utf8', **kwargs):
        if not self.is_writable_file():
            raise PathSecurityError(
                f'Cannot write file because it is outside permitted locations:  "{self.as_posix()}"'
            )
        return super().write_text(data, encoding=encoding, **kwargs)




def latexminted_config_read_bytes() -> bytes:
    '''
    Read the minted config file in the user home directory.  This is a dot
    file and thus cannot be accessed via `RestrictedPath`.
    '''
    return pathlib.Path('~/.latexminted_config').expanduser().read_bytes()




cwd_path: RestrictedPath = RestrictedPath.cwd().resolve()

# Ignore $TEXMFOUTPUT in determining location to write temp files, since
# it's a fallback if the current directory isn't writable.  $TEXMFOUTPUT is
# only used for communicating error messages.
tempfiledir_path: RestrictedPath
_texmf_output_directory = os.getenv('TEXMF_OUTPUT_DIRECTORY')
if _texmf_output_directory:
    tempfiledir_path = RestrictedPath(_texmf_output_directory).resolve()
else:
    tempfiledir_path = cwd_path
del _texmf_output_directory

texmfoutput_path: RestrictedPath | None = None
_texmfoutput = os.getenv('TEXMFOUTPUT')
if _texmfoutput:
    texmfoutput_path = RestrictedPath(_texmfoutput).resolve()
del _texmfoutput

# Version of `tempfiledir_path` to use within `\input` in LaTeX
input_tempfiledir_path_str: str
try:
    input_tempfiledir_path_str = tempfiledir_path.relative_to(cwd_path).as_posix()
except ValueError:
    input_tempfiledir_path_str = tempfiledir_path.as_posix()
if input_tempfiledir_path_str == '.':
    input_tempfiledir_path_str = ''
elif not input_tempfiledir_path_str.endswith('/'):
    input_tempfiledir_path_str += '/'
