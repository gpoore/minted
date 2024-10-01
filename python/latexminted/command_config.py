# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from latexrestricted import PathSecurityError
from .command_clean import clean_initial_temp
from .messages import Messages
from .restricted import MintedTempRestrictedPath
from .version import __version_info__




def config(*, md5: str, timestamp: str, debug: bool, messages: Messages, data: dict[str, str] | None):
    config_file_name = f'_{md5}.config.minted'

    clean_initial_temp(md5=md5)

    config_lines = []
    minted_executable_version = f'{__version_info__.major}.{__version_info__.minor}.{__version_info__.micro}'
    config_lines.append(rf'\gdef\minted@executable@version{{{minted_executable_version}}}%')
    config_lines.append(rf'\gdef\minted@executable@timestamp{{{timestamp}}}%')
    if data is not None:
        tex_timestamp: str = data['timestamp']
        config_lines.append(rf'\gdef\minted@config@timestamp{{{tex_timestamp}}}%')

    for openout_root in MintedTempRestrictedPath.tex_openout_roots():
        try:
            with (openout_root / config_file_name).open('w', encoding='utf8') as config_file:
                if data is None:
                    config_file.write('\n'.join(config_lines))
                    return
                tex_cachedir: str = data['cachedir']
                tex_cachepath: str
                if MintedTempRestrictedPath(tex_cachedir).is_absolute() or openout_root == MintedTempRestrictedPath.tex_cwd():
                    tex_cachepath = tex_cachedir
                else:
                    try:
                        tex_cachepath = (openout_root / tex_cachedir).relative_to(MintedTempRestrictedPath.tex_cwd()).as_posix()
                    except ValueError:
                        tex_cachepath = (openout_root / tex_cachedir).as_posix()
                if tex_cachepath and not tex_cachepath.endswith('/'):
                    tex_cachepath += '/'
                config_lines.append(rf'\gdef\minted@config@cachepath{{{tex_cachepath}}}%')
                config_file.write('\n'.join(config_lines))
                return
        except (PermissionError, PathSecurityError):
            continue
