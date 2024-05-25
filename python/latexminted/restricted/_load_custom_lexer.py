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
from ..err import CustomLexerError, CustomLexerSecurityError, MissingLatexMintedRCError
from ._latexminted_config import load_latexminted_config
from ._restricted_pathlib import RestrictedPath




def load_custom_lexer(lexer: str) -> type[Lexer]:
    lexer_path = RestrictedPath(lexer)
    class_name: str = 'CustomLexer'
    if ':' in lexer_path.name:
        file_name, class_name = lexer_path.name.split(':', 1)
        lexer_path = lexer_path.parent / file_name
    if not lexer_path.name.endswith('.py'):
        raise CustomLexerError('Custom lexers must be in *.py files')

    latexminted_config_data = load_latexminted_config()
    if latexminted_config_data is None:
        raise MissingLatexMintedRCError('Missing or invalid ~/.latexminted_config; custom lexers are disabled')
    if 'custom_lexers' not in latexminted_config_data:
        raise CustomLexerSecurityError('No custom lexers are enabled in ~/.latexminted_config')

    try:
        lexer_bytes = lexer_path.read_bytes()
    except FileNotFoundError:
        raise CustomLexerError(f'Custom lexer "{lexer_path.name}" was not found')
    except PermissionError:
        raise CustomLexerError(f'Insufficient permission to open custom lexer "{lexer_path.name}"')

    hasher = hashlib.sha256()
    hasher.update(lexer_bytes)
    hash = hasher.hexdigest()
    if latexminted_config_data['custom_lexers'].get(lexer_path.name, '').lower() != hash:
        raise CustomLexerSecurityError(
            f'Custom lexer "{lexer_path.name}" is not enabled in ~/.latexminted_config; check that SHA-256 hash is present and updated'
        )

    namespace = {}
    try:
        exec(lexer_bytes, namespace)
    except Exception:
        raise CustomLexerError(f'Failed to exec custom lexer "{lexer}"; check the lexer file for errors')
    if class_name not in namespace:
        raise CustomLexerError(f'Custom lexer class "{class_name}" was not created by "{lexer_path.name}"')
    lexer_class = namespace[class_name]
    if not issubclass(lexer_class, Lexer):
        raise CustomLexerError(f'Custom lexer class "{class_name}" is not a subclass of Pygments Lexer class')
    return lexer_class
