# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import re
try:
    from typing import Self
except ImportError:
    pass
from ..err import PathSecurityError
from ._anypath import AnyPath
from ._latex_config import latex_config



_cwd_anypath = AnyPath(latex_config.tex_cwd)
if latex_config.TEXMFOUTPUT:
    _TEXMFOUTPUT_anypath_resolved = AnyPath(latex_config.TEXMFOUTPUT).resolve()
else:
    _TEXMFOUTPUT_anypath_resolved = None
if latex_config.TEXMF_OUTPUT_DIRECTORY:
    _TEXMF_OUTPUT_DIRECTORY_anypath_resolved = AnyPath(latex_config.TEXMF_OUTPUT_DIRECTORY).resolve()
else:
    _TEXMF_OUTPUT_DIRECTORY_anypath_resolved = None


class RestrictedPath(type(AnyPath())):
    '''
    Subclass of `pathlib.Path` (which is system-dependent) that restricts file
    operations to be consistent with TeX restricted shell escape security
    requirements.  For this to be effective, all file operations must go
    through this class; it must not be bypassed with other modules such as
    `os` and `shutil` or functions such as `open()`.

     *  Reading:  Restricted to `.read_text()`, `.read_bytes()`, and
        `.open()`.  Permitted file locations and file names depend on variable
        `openin_any` in `texmf.cnf` config files.

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

    Differences from TeX's file system security (for example, see
    https://www.tug.org/texinfohtml/kpathsea.html#Safe-filenames-1):

     *  TeX's security settings for reading and writing files depend on
        analyzing file paths as strings; the actual file system is never
        consulted.  The default security setting for writing restricts
        absolute paths to files within $TEXMF_OUTPUT_DIRECTORY and
        $TEXMFOUTPUT.  Paths cannot contain `..` to access parent directories,
        even if the location referred to is allowed.  As a result, relative
        paths are restricted to paths under the current working directory
        (plus $TEXMF_OUTPUT_DIRECTORY and $TEXMFOUTPUT, depending on document
        and system configuration).  Symbolic links are not resolved, so they
        can be used to access locations outside the current working directory,
        $TEXMF_OUTPUT_DIRECTORY, and $TEXMFOUTPUT.

        File system security is determined by `openout_any` and `openin_any`
        settings in `texmf.cnf` for TeX Live, and from
        `[Core]AllowUnsafeInputFiles` and `[Core]AllowUnsafeOutputFiles` in
        `miktex.ini` for MiKTeX.

     *  `RestrictedPath` security settings depend on resolving paths using the
        file system.  Paths are converted into absolute paths with all
        symlinks resolved, and only then are compared with permitted locations
        for reading and writing.  Absolute paths and paths containing `..` are
        always accepted for any permitted location.  Symbolic links are
        resolved before determining whether a path is permitted, so they
        cannot be used to access locations outside the current working
        directory, $TEXMF_OUTPUT_DIRECTORY, and $TEXMFOUTPUT.
    '''

    _fs_read_dotfiles: bool = latex_config.can_read_dotfiles
    _fs_read_roots: set[AnyPath] | None
    if latex_config.can_read_anywhere:
        _fs_read_roots = None
    else:
        _fs_read_roots = set()
        _fs_read_roots.add(_cwd_anypath)
        for p in (_TEXMFOUTPUT_anypath_resolved, _TEXMF_OUTPUT_DIRECTORY_anypath_resolved):
            if p is not None:
                _fs_read_roots.add(p)

    _fs_write_dotfiles: bool = latex_config.can_write_dotfiles
    _fs_write_roots: set[AnyPath] | None
    # Use the code below if this is separated out into a separate
    # `latexrestricted` package with `RestrictedPath` as the base class for
    # various kinds of restricted paths
    # ------------------------------------------------------------------------
    # if latex_config.can_write_anywhere:
    #     _fs_write_roots = None
    # else:
    #     _fs_write_roots = set()
    #     _fs_write_roots.add(_cwd_anypath)
    #     for p in (_TEXMFOUTPUT_anypath_resolved, _TEXMF_OUTPUT_DIRECTORY_anypath_resolved):
    #         if p is not None:
    #             _fs_write_roots.add(p)
    _fs_write_roots = set()
    _fs_write_roots.add(_cwd_anypath)
    for p in (_TEXMFOUTPUT_anypath_resolved, _TEXMF_OUTPUT_DIRECTORY_anypath_resolved):
        if p is not None:
            _fs_write_roots.add(p)

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

    def is_readable_dir(self) -> bool:
        if self not in self._checked_readable_dir_set:
            resolved = self.resolve()
            if self._fs_read_roots is None or any(resolved.is_relative_to(p) for p in self._fs_read_roots):
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
            if self._fs_write_roots is None or any(resolved.is_relative_to(p) for p in self._fs_write_roots):
                self._is_writable_dir_set.add(self)
            self._checked_writable_dir_set.add(self)
        return self in self._is_writable_dir_set

    def is_writable_file(self) -> bool:
        if self not in self._checked_writable_file_set:
            resolved = self.resolve()
            if (resolved.parent.is_writable_dir() and
                    (self._fs_write_dotfiles or not resolved.name.startswith('.')) and
                    not any(resolved.name.endswith(ext) for ext in latex_config.prohibited_write_file_extensions) and
                    self._writable_filename_re.fullmatch(resolved.name)):
                self._is_writable_file_set.add(self)
            self._checked_writable_file_set.add(self)
        return self in self._is_writable_file_set


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


    @classmethod
    def tex_cwd(cls) -> Self:
        return cls(_cwd_anypath)

    @classmethod
    def TEXMFOUTPUT(cls) -> Self | None:
        if _TEXMFOUTPUT_anypath_resolved is None:
            return None
        return cls(_TEXMFOUTPUT_anypath_resolved)

    @classmethod
    def TEXMF_OUTPUT_DIRECTORY(cls) -> Self | None:
        if _TEXMF_OUTPUT_DIRECTORY_anypath_resolved is None:
            return None
        return cls(_TEXMF_OUTPUT_DIRECTORY_anypath_resolved)

    @classmethod
    def openout_roots(cls) -> list[Self]:
        openout_roots: list[Self] = []
        TEXMF_OUTPUT_DIRECTORY = cls.TEXMF_OUTPUT_DIRECTORY()
        if TEXMF_OUTPUT_DIRECTORY:
            openout_roots.append(TEXMF_OUTPUT_DIRECTORY)
        else:
            openout_roots.append(cls.tex_cwd())
        TEXMFOUTPUT = cls.TEXMFOUTPUT()
        if TEXMFOUTPUT and TEXMFOUTPUT not in openout_roots:
            openout_roots.append(TEXMFOUTPUT)
        return openout_roots

    @classmethod
    def all_writable_roots(cls) -> set[Self]:
        all_writable_roots: set[Self] = set()
        all_writable_roots.add(cls.tex_cwd())
        TEXMF_OUTPUT_DIRECTORY = cls.TEXMF_OUTPUT_DIRECTORY()
        if TEXMF_OUTPUT_DIRECTORY:
            all_writable_roots.add(TEXMF_OUTPUT_DIRECTORY)
        TEXMFOUTPUT = cls.TEXMFOUTPUT()
        if TEXMFOUTPUT:
            all_writable_roots.add(TEXMFOUTPUT)
        return all_writable_roots




def latexminted_config_read_bytes() -> list[bytes]:
    '''
    Read minted config files from the user home directory and TEXMFHOME.
    These are dot files and thus cannot be accessed via `RestrictedPath`.
    '''
    config_bytes_list = []
    try:
        config_bytes_list.append(AnyPath('~/.latexminted_config').expanduser().read_bytes())
    except (FileNotFoundError, PermissionError):
        pass
    latex_config_texmf = latex_config.kpsewhich_find_config_file('.latexminted_config')
    if latex_config_texmf:
        try:
            config_bytes_list.append(AnyPath(latex_config_texmf).read_bytes())
        except (FileNotFoundError, PermissionError):
            pass
    return config_bytes_list
