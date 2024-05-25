# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from typing import Any
from ast import literal_eval
from json import loads as json_loads
try:
    from tomllib import loads as toml_loads
except ImportError:
    toml_loads = None

from ._restricted_pathlib import latexminted_config_read_bytes




_cache = {}

def load_latexminted_config() -> dict[str, Any] | None:
    if 'data' in _cache:
        return _cache['data']

    try:
        latexminted_config_bytes = latexminted_config_read_bytes()
    except (FileNotFoundError, PermissionError):
        _cache['data'] = None
        return _cache['data']

    try:
        latexminted_config_str = latexminted_config_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        _cache['data'] = None
        return _cache['data']

    loaders = [json_loads, literal_eval]
    if toml_loads is not None:
        loaders.append(toml_loads)
    data: dict[str, Any] | None = None
    for loader in loaders:
        try:
            data = loader(latexminted_config_str)
        except Exception:
            continue
        else:
            if not isinstance(data, dict) or not all(isinstance(k, str) for k in data):
                data = None
            if data is not None and 'custom_lexers' in data:
                if not all(isinstance(k, str) and isinstance(v, str) for k, v in data['custom_lexers'].items()):
                    data = None
            break
    _cache['data'] = data
    return _cache['data']
