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
from ast import literal_eval
from collections import defaultdict
from json import loads as json_loads
from typing import Literal
try:
    from tomllib import loads as toml_loads
except ImportError:
    toml_loads = None
from latexrestricted import latex_config, PathSecurityError, ResolvedRestrictedPath
from ..err import LatexMintedConfigError




class LatexMintedConfigPath(ResolvedRestrictedPath):
    '''
    Class for `.latexminted_config` config files.  Only allows reading files
    that are not writable by LaTeX.
    '''
    def readable_dir(self):
        raise NotImplementedError

    def readable_file(self) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        if self.name != '.latexminted_config':
            return (
                False,
                f'Cannot load config file "{self.as_posix()}"; only file name ".latexminted_config" is supported'
            )
        is_latex_writable, _ = ResolvedRestrictedPath(self).writable_file()
        if is_latex_writable:
            return (
                False,
                f'Cannot load config file "{self.as_posix()}" because LaTeX settings make it writable by LaTeX'
            )
        return (True, None)

    def writable_dir(self):
        raise NotImplementedError

    def writable_file(self):
        raise NotImplementedError


_file_extension_re = re.compile(r'\.[0-9A-Za-z]+')


class LatexMintedConfigSecurity(object):
    def __init__(self):
        self._enable_cwd_config: bool = False
        self._file_path_analysis: Literal['resolve'] | Literal['string'] = 'resolve'
        self._permitted_pathext_file_extensions: frozenset[str] | None = None

    @property
    def enable_cwd_config(self):
        return self._enable_cwd_config

    @property
    def file_path_analysis(self):
        return self._file_path_analysis

    @property
    def permitted_pathext_file_extensions(self):
        return self._permitted_pathext_file_extensions

    def update(self, **kwargs):
        enable_cwd_config = kwargs.pop('enable_cwd_config', None)
        if enable_cwd_config is not None:
            if enable_cwd_config not in (True, False):
                raise LatexMintedConfigError('"security.enable_cwd_config" must be boolean')
            self._enable_cwd_config = enable_cwd_config

        file_path_analysis = kwargs.pop('file_path_analysis', None)
        if file_path_analysis is not None:
            if file_path_analysis not in ('resolve', 'string'):
                raise LatexMintedConfigError('"security.file_path_analysis" must be "resolve" or "string"')
            self._file_path_analysis = file_path_analysis

        permitted_pathext = kwargs.pop('permitted_pathext_file_extensions', None)
        if permitted_pathext is not None:
            if not isinstance(permitted_pathext, list) or not all(isinstance(x, str) for x in permitted_pathext):
                raise LatexMintedConfigError(
                    '"security.permitted_pathext_file_extensions" must be a list of strings'
                )
            if not all(_file_extension_re.fullmatch(x) for x in permitted_pathext):
                raise LatexMintedConfigError(
                    '"security.permitted_pathext_file_extensions" must be a list of file extensions ".<ext>"'
                )
            self._permitted_pathext_file_extensions = frozenset(x.lower() for x in permitted_pathext)

        if kwargs:
            unknowns_keys = ', '.join(f'"{k}"' for k in kwargs)
            raise LatexMintedConfigError(f'"security" contains unknown keys {unknowns_keys}')


class LatexMintedConfig(object):
    def __init__(self):
        self._custom_lexers: dict[str, set[str]] = defaultdict(set)
        self._did_load_config_file: bool = False
        self._security: LatexMintedConfigSecurity = LatexMintedConfigSecurity()
        self._tex_cwd = LatexMintedConfigPath(latex_config.tex_cwd)

        config_name = '.latexminted_config'
        self._load(LatexMintedConfigPath.home() / config_name)
        if latex_config.TEXMFHOME:
            self._load(LatexMintedConfigPath(latex_config.TEXMFHOME) / config_name)
        if self._security.enable_cwd_config:
            self._load(self._tex_cwd / config_name)

    def is_custom_lexer_enabled(self, *, name: str, hash: str):
        return hash.lower() in self._custom_lexers[name]

    @property
    def did_load_config_file(self):
        return self._did_load_config_file

    @property
    def security(self):
        return self._security


    _loaders = [json_loads, literal_eval]
    if toml_loads is not None:
        _loaders.append(toml_loads)

    def _load(self, path: LatexMintedConfigPath):
        try:
            data_str = path.read_text(encoding='utf-8-sig')
        except FileNotFoundError:
            return
        except PermissionError:
            raise LatexMintedConfigError(
                f'Permission error prevented access to config file "{path.as_posix()}"'
            )
        except PathSecurityError as e:
            raise LatexMintedConfigError(str(e))
        except UnicodeDecodeError as e:
            raise LatexMintedConfigError(
                f'Failed to decode config file "{path.as_posix()}":  {e}'
            )

        for loader in self._loaders:
            try:
                data = loader(data_str)
                break
            except Exception:
                continue
        else:
            raise LatexMintedConfigError(
                f'Invalid config file "{path.as_posix()}":  could not deserialize data '
                '(check for syntax errors and similar issues)'
            )

        if not isinstance(data, dict) or not all(isinstance(k, str) for k in data):
            raise LatexMintedConfigError(
                f'Invalid config file "{path.as_posix()}":  data must be a dict with string keys'
            )

        custom_lexers = data.pop('custom_lexers', None)
        if custom_lexers:
            if not isinstance(custom_lexers, dict):
                raise LatexMintedConfigError(
                    f'Invalid config file "{path.as_posix()}":  "custom_lexers" must be a dict with string keys and '
                    'with values that are either strings or lists of strings'
                )
            for k, v in custom_lexers.items():
                if not isinstance(k, str):
                    raise LatexMintedConfigError(
                        f'Invalid config file "{path.as_posix()}":  "custom_lexers" must be a dict with string keys'
                    )
                if isinstance(v, str):
                    self._custom_lexers[k].add(v.lower())
                elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                    self._custom_lexers[k].update(v_i.lower() for v_i in v)
                else:
                    raise LatexMintedConfigError(
                        f'Invalid config file "{path.as_posix()}":  "custom_lexers" must be a dict '
                        'with values that are either strings or lists of strings'
                    )

        security = data.pop('security', None)
        if security:
            if path.is_relative_to(self._tex_cwd):
                raise LatexMintedConfigError(
                    f'Invalid config file "{path.as_posix()}": "security" cannot be modified '
                    'by a config file in the TeX working directory'
                )
            if not (isinstance(security, dict) and all(isinstance(k, str) for k in security)):
                raise LatexMintedConfigError(
                    f'Invalid config file "{path.as_posix()}":  "security" must be a dict with string keys'
                )
            try:
                self._security.update(**security)
            except LatexMintedConfigError as e:
                raise LatexMintedConfigError(f'Invalid config file "{path.as_posix()}":  {e}')

        if data:
            unknowns_keys = ', '.join(f'"{k}"' for k in data)
            raise LatexMintedConfigError(
                f'Invalid config file "{path.as_posix()}":  unknown keys {unknowns_keys}'
            )

        self._did_load_config_file = True


latexminted_config = LatexMintedConfig()
