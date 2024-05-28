# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from .command_clean import clean_temp
from .messages import Messages
from .restricted import cwd_path, input_tempfiledir_path_str, tempfiledir_path, RestrictedPath
from .version import __version_info__




def config(*, md5: str, timestamp: str, messages: Messages, data: dict[str, str] | None):
    config_file_name = f'_{md5}.config.minted'

    clean_temp(md5=md5)

    config_lines = []
    minted_executable_version = f'{__version_info__.major}.{__version_info__.minor}.{__version_info__.micro}'
    config_lines.append(rf'\gdef\minted@executable@version{{{minted_executable_version}}}%')
    config_lines.append(rf'\gdef\minted@executable@timestamp{{{timestamp}}}%')
    if data is not None:
        tex_timestamp: str = data['timestamp']
        config_lines.append(rf'\gdef\minted@config@timestamp{{{tex_timestamp}}}%')
        tex_cachepath: str
        tex_cachedir: str = data['cachedir']
        if RestrictedPath(tex_cachedir).is_absolute() or not input_tempfiledir_path_str:
            tex_cachepath = tex_cachedir
        else:
            if tex_cachedir.startswith('./'):
                tex_cachedir = tex_cachedir[2:]
            tex_cachepath = f'{input_tempfiledir_path_str}{tex_cachedir}'
        if not tex_cachepath.endswith('/'):
            tex_cachepath += '/'
        config_lines.append(rf'\gdef\minted@config@cachepath{{{tex_cachepath}}}%')

    try:
        (tempfiledir_path / config_file_name).write_text('\n'.join(config_lines))
    except PermissionError:
        messages.append_error('Insufficient permission to write minted config file')
    else:
        return

    if data is None and tempfiledir_path is not cwd_path:
        try:
            (cwd_path / config_file_name).write_text('\n'.join(config_lines))
        except PermissionError:
            messages.append_error('Insufficient permission to write minted config file')
