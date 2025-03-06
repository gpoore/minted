# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from latex2pydata import loads as latex2pydata_loads
from typing import Any
from .messages import Messages
from .restricted import MintedTempRestrictedPath




def load_data(*, md5: str, messages: Messages, timestamp: str, command: str) -> tuple[list[dict[str, Any]] | dict[str, Any], MintedTempRestrictedPath] | None:
    data_file_name: str = f'_{md5}.data.minted'

    data_text: str | None = None
    for read_path in MintedTempRestrictedPath.tex_openout_roots()[:-1]:
        data_path = read_path / data_file_name
        try:
            data_text = data_path.read_text(encoding='utf8')
        except (FileNotFoundError, PermissionError):
            continue
        except UnicodeDecodeError:
            messages.append_error(rf'Failed to decode file \detokenize{{"{data_file_name}"}} (expected UTF-8)')
            return None
    if data_text is None:
        data_path = MintedTempRestrictedPath.tex_openout_roots()[-1] / data_file_name
        try:
            data_text = data_path.read_text(encoding='utf8')
        except FileNotFoundError:
            messages.append_error(rf'Failed to find file \detokenize{{"{data_file_name}"}}')
        except PermissionError:
            messages.append_error(rf'Insufficient permission to open file \detokenize{{"{data_file_name}"}}')
        except UnicodeDecodeError:
            messages.append_error(rf'Failed to decode file \detokenize{{"{data_file_name}"}} (expected UTF-8)')
    if data_text is None:
        return None

    try:
        data = latex2pydata_loads(data_text, schema={'cachefiles': 'list[str]'}, schema_missing='verbatim')
    except Exception as e:
        messages.append_error(
            rf'Failed to load data from file \detokenize{{"{data_file_name}"}} (see \detokenize{{"{messages.errlog_file_name}"}})'
        )
        messages.append_errlog(e)
        return None
    if isinstance(data, dict):
        if command != data['command']:
            messages.append_error(
                rf'''minted data file \detokenize{{"{data_file_name}"}} is for "{data['command']}", but expected "{command}"'''
            )
            return None
        if timestamp != data['timestamp']:
            messages.append_error(
                rf'minted data file \detokenize{{"{data_file_name}"}} has incorrect timestamp'
            )
            return None
    elif isinstance(data, list):
        if command != 'batch':
            messages.append_error(
                rf'''minted data file \detokenize{{"{data_file_name}"}} is for "batch", but expected "{command}"'''
            )
            return None
        valid_commands = set(['styledef', 'highlight', 'clean'])
        if not all(d['command'] in valid_commands for d in data):
            messages.append_error(
                rf'''minted data file \detokenize{{"{data_file_name}"}} is for "batch", but contains invalid data'''
            )
            return None
        if data and timestamp != data[0]['timestamp']:
            messages.append_error(
                rf'minted data file \detokenize{{"{data_file_name}"}} has incorrect timestamp'
            )
            return None
    else:
        messages.append_error(
            rf'minted data file \detokenize{{"{data_file_name}"}} contains unexpected data type "{type(data)}"'
        )
        return None
    return (data, data_path)
