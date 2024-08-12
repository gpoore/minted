# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import hashlib
from pygments.lexer import Lexer
from latexrestricted import PathSecurityError
from ..err import CustomLexerError
from ._latexminted_config import latexminted_config
from ._restricted_pathlib import MintedTempRestrictedPath




def load_custom_lexer(lexer: str) -> type[Lexer]:
    if not latexminted_config.did_load_config_file:
        raise CustomLexerError('Missing ".latexminted_config"; custom lexers are disabled')

    lexer_path = MintedTempRestrictedPath(lexer)
    class_name: str = 'CustomLexer'
    if ':' in lexer_path.name:
        file_name, class_name = lexer_path.name.split(':', 1)
        lexer_path = lexer_path.parent / file_name
    if not lexer_path.name.lower().endswith('.py'):
        raise CustomLexerError(f'Custom lexer "{lexer}" is not a *.py file')

    try:
        lexer_bytes = lexer_path.read_bytes()
    except FileNotFoundError:
        raise CustomLexerError(f'Custom lexer "{lexer}" was not found')
    except PermissionError:
        raise CustomLexerError(f'Insufficient permission to open custom lexer "{lexer_path.as_posix()}"')
    except PathSecurityError as e:
        raise CustomLexerError(str(e))

    hasher = hashlib.sha256()
    hasher.update(lexer_bytes)
    hash = hasher.hexdigest()
    if not latexminted_config.is_custom_lexer_enabled(name=lexer_path.name, hash=hash):
        raise CustomLexerError(
            f'Custom lexer "{lexer_path.name}" is not enabled in ".latexminted_config"; '
            'check that SHA-256 hash is present and updated'
        )

    try:
        lexer_str = lexer_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise CustomLexerError(f'Failed to decode custom lexer file "{lexer}" as UTF-8')

    namespace = {}
    try:
        exec(lexer_str, namespace)
    except Exception:
        raise CustomLexerError(f'Failed to exec custom lexer "{lexer}"; check the lexer file for errors')
    if class_name not in namespace:
        raise CustomLexerError(f'Custom lexer class "{class_name}" was not created by "{lexer}"')
    lexer_class = namespace[class_name]
    if not issubclass(lexer_class, Lexer):
        raise CustomLexerError(
            f'Custom lexer class "{class_name}" from "{lexer}" is not a subclass of the Pygments Lexer class'
        )
    return lexer_class
