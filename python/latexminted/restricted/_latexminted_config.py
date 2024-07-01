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
    if 'config' in _cache:
        return _cache['config']

    config_bytes_list = latexminted_config_read_bytes()
    if not config_bytes_list:
        _cache['config'] = None
        return _cache['config']

    config_str_list = []
    for config_bytes in config_bytes_list:
        try:
            config_str_list.append(config_bytes.decode('utf-8-sig'))
        except UnicodeDecodeError:
            _cache['config'] = None
            return _cache['config']

    loaders = [json_loads, literal_eval]
    if toml_loads is not None:
        loaders.append(toml_loads)
    config = {}
    for config_str in config_str_list:
        for loader in loaders:
            try:
                data = loader(config_str)
            except Exception:
                continue
            else:
                if not isinstance(data, dict) or not all(isinstance(k, str) for k in data):
                    break
                if 'custom_lexers' in data:
                    if not all(isinstance(k, str) and isinstance(v, str) for k, v in data['custom_lexers'].items()):
                        break
                for k, v in data.items():
                    if isinstance(v, dict):
                        if k in config and isinstance(config[k], dict):
                            config[k].update(v)
                        else:
                            config[k] = v
                    elif isinstance(v, list):
                        if k in config and isinstance(config[k], list):
                            config[k].extend(v)
                        else:
                            config[k] = v
                    else:
                        config[k] = v
                break
    if config:
        _cache['config'] = config
    else:
        _cache['config'] = None
    return _cache['config']
