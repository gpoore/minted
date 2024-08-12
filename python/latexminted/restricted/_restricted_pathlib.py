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
from typing import Literal
from latexrestricted import SafeWriteStringRestrictedPath, SafeWriteResolvedRestrictedPath
from ._latexminted_config import latexminted_config




# `[0-9a-zA-Z_-]+` covers temp file names `_<MD5 hash>` plus code cache file
# names `<MD5 hash>` plus style names `<style name>`.
_minted_temp_file_re = re.compile(r'[0-9a-zA-Z_-]+\.(?:config|data|errlog|highlight|index|message|style)\.minted')


if latexminted_config.security.file_path_analysis == 'resolve':
    MintedBaseRestrictedPath = SafeWriteResolvedRestrictedPath
elif latexminted_config.security.file_path_analysis == 'string':
    MintedBaseRestrictedPath = SafeWriteStringRestrictedPath
else:
    raise TypeError


class MintedTempRestrictedPath(MintedBaseRestrictedPath):
    '''
    Class for temp files, including cache files.
    '''
    def writable_file(self) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        try:
            return self._writable_file_cache[self.cache_key]
        except KeyError:
            if _minted_temp_file_re.fullmatch(self.name):
                return super().writable_file()
            self._writable_file_cache[self.cache_key] = (
                False,
                f'file name "{self.name}" does not match the regular expression for minted temp and cache files'
            )
            return self._writable_file_cache[self.cache_key]


class MintedCodeRestrictedPath(MintedBaseRestrictedPath):
    '''
    Class for source code that is extracted from a document and saved in
    external files.
    '''
    if latexminted_config.security.permitted_pathext_file_extensions is not None:
        _prohibited_write_file_extensions = MintedBaseRestrictedPath.prohibited_write_file_extensions()
        if _prohibited_write_file_extensions is not None:
            _prohibited_write_file_extensions = frozenset(
                _prohibited_write_file_extensions - latexminted_config.security.permitted_pathext_file_extensions
            )

        @classmethod
        def prohibited_write_file_extensions(cls) -> frozenset[str] | None:
            return cls._prohibited_write_file_extensions

    def writable_dir(self) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        try:
            return self._writable_dir_cache[self.cache_key]
        except KeyError:
            # Require source code to be saved in a subdirectory of an output
            # root, rather than at the root itself.  If the code is not in a
            # location that is likely to be used as a current working
            # directory in a shell, then there is reduced potential for
            # unintentional code execution in the event that the user disables
            # other security settings.  This checks paths in both
            # raw and resolved forms to force increased security regardless of
            # `RestrictedPath` base class.
            if any(code_path == root_path for code_path in set([self, self.resolved()])
                   for root_path in self.tex_roots_with_resolved()):
                self._writable_dir_cache[self.cache_key] = (
                    False,
                    f'extracted code file "{self.as_posix()}" is not permitted in the TeX working directory, '
                    'TEXMF_OUTPUT_DIRECTORY, or TEXMFOUTPUT; it must be in a designated subdirectory'
                )
                return self._writable_dir_cache[self.cache_key]
            return super().writable_dir()
