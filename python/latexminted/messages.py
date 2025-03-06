# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import textwrap
import traceback
from typing import Any
from .restricted import MintedTempRestrictedPath




class Messages(object):
    def __init__(self, *, md5: str):
        self._md5 = md5
        self._warnings: list[str] = []
        self._errors: list[str] = []
        self._errlogs: list[str] = []
        self.message_file_name: str = f'_{self._md5}.message.minted'
        self.errlog_file_name: str = f'_{self._md5}.errlog.minted'
        self._jobname: str | None = None
        self._currentfilepath: str | None = None
        self._currentfile: str | None = None
        self._inputlineno: str | None = None


    def set_context(self, data: dict[str, Any] | None = None):
        if data is None:
            self._jobname = None
            self._currentfilepath = None
            self._currentfile = None
            self._inputlineno = None
        else:
            self._jobname = data['jobname']
            self._currentfilepath = data['currentfilepath']
            self._currentfile = data['currentfile']
            self._inputlineno = data['inputlineno']

    def _add_context(self, message: str, latex: bool = False) -> str:
        if self._jobname is None:
            if latex:
                return message
            return f'''{'='*80}\n\n{message}'''

        if self._currentfilepath:
            path = self._currentfilepath
            if not MintedTempRestrictedPath(path).is_absolute() and not path.startswith('.'):
                path = f'./{path}'
            if not path.endswith('/'):
                path += '/'
        else:
            path = './'
        if self._currentfile:
            name = self._currentfile
        else:
            name = self._jobname
            if (name.startswith('"') and name.endswith('"')) or (name.startswith("'") and name.endswith("'")):
                name = name[1:-1]
        number = self._inputlineno
        if latex:
            return rf'^^J => \detokenize{{{path}{name}:{number}:}} {message}'
        return f'''{'='*80}\n{path}{name}:{number}\n{'-'*80}\n{message}'''


    def append_warning(self, message: str):
        self._warnings.append(self._add_context(message, latex=True))

    def append_error(self, message: str):
        self._errors.append(self._add_context(message, latex=True))

    def append_errlog(self, message: str | Exception):
        if isinstance(message, str):
            if not message.endswith('\n'):
                message += '\n'
            self._errlogs.append(self._add_context(message))
        elif isinstance(message, Exception):
            self._errlogs.append(self._add_context(
                textwrap.dedent(''.join(traceback.format_tb(message.__traceback__)))
            ))
        else:
            raise TypeError

    def has_errors(self) -> bool:
        return len(self._errors) > 0


    def communicate(self):
        if not self._warnings and not self._errors and not self._errlogs:
            return

        message_lines = []
        if self._warnings:
            message_lines.append(r'\def\minted@exec@warning{%')
            for message in self._warnings:
                message_lines.append(rf'  \minted@warning{{{message}}}%')
            message_lines.append('}%')
        if self._errors:
            message_lines.append(r'\def\minted@exec@error{%')
            for message in self._errors:
                message_lines.append(rf'  \minted@error{{{message}}}%')
            message_lines.append(r'}%')

        if message_lines:
            for write_path in MintedTempRestrictedPath.tex_openout_roots():
                try:
                    (write_path / self.message_file_name).write_text('\n'.join(message_lines), encoding='utf8')
                except PermissionError:
                    continue
                else:
                    break

        if self._errlogs:
            errlogs = '\n'.join(self._errlogs)
            if not errlogs.endswith('\n'):
                errlogs += '\n'
            if not errlogs.endswith('\n\n'):
                errlogs += '\n'
            for write_path in MintedTempRestrictedPath.tex_openout_roots():
                try:
                    with (write_path / self.errlog_file_name).open('a', encoding='utf8') as f:
                        f.write(errlogs)
                except PermissionError:
                    continue
                else:
                    break
