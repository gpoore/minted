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
import re
import sys
import textwrap
from typing import Any
from pygments import highlight as pygments_highlight
from pygments.formatters import LatexFormatter
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from .err import (
    PathSecurityError,
    SubprocessExecutableNotFoundError, SubprocessExecutablePathSecurityError,
    MissingLatexMintedRCError,
    CustomLexerError, CustomLexerSecurityError,
)
from .messages import Messages
from .restricted import load_custom_lexer, RestrictedPath, restricted_run




# Sets and dicts for checking Python-related options and converting values to
# Python types
bool_keys: set[str] = set([
    'autogobble',
    'codetagify',
    'funcnamehighlighting',
    'mathescape',
    'python3',
    'rangeregexdotall',
    'rangeregexmultiline',
    'startinline',
    'stripall',
    'stripnl',
    'texcl',
    'texcomments',
])
nonnegative_int_re = re.compile('[1-9][0-9]*|0')
nonnegative_int_or_none_keys: set[str] = set([
    'gobble',
])
positive_int_re = re.compile('[1-9][0-9]*')
positive_int_keys: set[str] = set([
    'rangeregexmatchnumber',
])
other_keys_value_sets: dict[str, set[str]] = {
    'keywordcase': set(['lower', 'upper' or 'capitalize']),
}
other_keys_unchecked_str_value: set[str] = set([
    'commandprefix',
    'encoding',
    'escapeinside',
    'lexer',
    'rangestartstring',
    'rangestartafterstring',
    'rangestopstring',
    'rangestopbeforestring',
    'rangeregex',
])
all_keys = bool_keys | nonnegative_int_or_none_keys | positive_int_keys | set(other_keys_value_sets) | other_keys_unchecked_str_value

# Key for manipulating code within Python
code_keys = set([
    'autogobble',
    'gobble',
    'rangestartstring',
    'rangestartafterstring',
    'rangestopstring',
    'rangestopbeforestring',
    'rangeregex',
    'rangeregexmatchnumber',
    'rangeregexdotall',
    'rangeregexmultiline',
])
# Categorize Pygments options into lexer, filter, or formatter
lexer_keys: set[str] = set([
    'funcnamehighlighting',
    'python3',
    'startinline',
    'stripall',
    'stripnl',
])
filter_keys_no_options: set[str] = set([
    'codetagify',
])
filter_keys_one_option: dict[str, str] = {
    'keywordcase': 'case',
}
filter_keys = filter_keys_no_options | set(filter_keys_one_option)
formatter_keys: set[str] = set([
    'commandprefix',
    'escapeinside',
    'mathescape',
    'styleprefix',
    'texcl',
    'texcomments',
])
pygments_keys = lexer_keys | filter_keys | formatter_keys


def process_highlight_data(*, messages: Messages, data: dict[str, Any]) -> tuple[dict[str, Any], ...] | None:
    minted_opts: dict[str, str] = {k: v for k, v in data.items() if k != 'pyopt'}
    py_opts = {}
    code_opts = {}
    lexer_opts = {}
    filter_opts = {}
    formatter_opts = {}

    for k, v in data['pyopt'].items():
        if k in lexer_keys:
            current_opts = lexer_opts
        elif k in filter_keys:
            current_opts = filter_opts
        elif k in formatter_keys:
            current_opts = formatter_opts
        elif k in code_keys:
            current_opts = code_opts
        elif k in all_keys:
            current_opts = py_opts
        else:
            messages.append_error(rf'Key "{k}" is unknown and will be ignored')
            continue

        if k in bool_keys:
            if v in ('true', 'false'):
                current_opts[k] = v == 'true'
            else:
                messages.append_error(rf'Key "{k}" has invalid value \detokenize{{"{v}"}} (expected "true" or "false")')
        elif k in nonnegative_int_or_none_keys:
            if v == 'none':
                current_opts[k] = 0
            elif nonnegative_int_re.fullmatch(v):
                current_opts[k] = int(v)
            else:
                messages.append_error(rf'Key "{k}" has invalid value \detokenize{{"{v}"}} (expected non-negative integer or "none")')
        elif k in positive_int_keys:
            if positive_int_re.fullmatch(v):
                current_opts[k] = int(v)
            else:
                messages.append_error(rf'Key "{k}" has invalid value \detokenize{{"{v}"}} (expected positive integer)')
        elif k in other_keys_value_sets:
            if v in other_keys_value_sets[k]:
                current_opts[k] = v
            else:
                valid_options = ', '.join(f'"{opt}"' for opt in other_keys_value_sets[k])
                messages.append_error(rf'Key "{k}" has invalid value \detokenize{{"{v}"}} (expected {valid_options})')
        elif k in other_keys_unchecked_str_value:
            current_opts[k] = v
        else:
            messages.append_error(rf'Unknown key "{k}"')

    # Additional data processing
    if 'inputfilemdfivesum' in minted_opts:
        minted_opts['inputfilemdfivesum'] = minted_opts['inputfilemdfivesum'].lower()

    if messages.has_errors():
        return None
    return minted_opts, py_opts, code_opts, lexer_opts, filter_opts, formatter_opts




def load_input_file(*, messages: Messages, input_file: str, mdfivesum: str, encoding: str) -> str | None:
    input_file_path = RestrictedPath(input_file)
    try:
        input_file_bytes = input_file_path.read_bytes()
        hasher = hashlib.md5()
        hasher.update(input_file_bytes)
        if hasher.hexdigest() != mdfivesum:
            raise FileNotFoundError
        code_bytes = input_file_bytes
    except PermissionError:
        messages.append_error(rf'Insufficient permission to open file \detokenize{{"{input_file}"}}')
        return None
    except PathSecurityError:
        messages.append_error(rf'Cannot read file in prohibited location: \detokenize{{"{input_file}"}}')
        return None
    except FileNotFoundError:
        try:
            kpsewhich_proc = restricted_run(['kpsewhich', input_file])
        except SubprocessExecutableNotFoundError:
            messages.append_error(rf'Cannot locate file \detokenize{{"{input_file}"}} (kpsewhich unavailable)')
            return None
        except SubprocessExecutablePathSecurityError:
            messages.append_error(
                rf'Cannot use kpsewhich to locate file \detokenize{{"{input_file}"}} '
                r'when kpsewhich is located under the current directory, \detokenize{TEXMFOUTPUT}, '
                r'or \detokenize{TEXMF_OUTPUT_DIRECTORY}, or when these locations are under the same '
                r'directory as kpsewhich'
            )
            return None
        if kpsewhich_proc.returncode != 0:
            sys.stderr.buffer.write(kpsewhich_proc.stderr)
            messages.append_error(rf'Cannot locate file \detokenize{{"{input_file}"}} (kpsewhich failed)')
            return None
        try:
            kpsewhich_input_file_path = RestrictedPath(kpsewhich_proc.stdout.decode(sys.stdout.encoding).strip())
        except UnicodeDecodeError:
            messages.append_error(rf'Cannot locate file \detokenize{{"{input_file}"}} (could not decode kpsewhich output)')
            return None
        try:
            kpsewhich_input_file_bytes = kpsewhich_input_file_path.read_bytes()
        except FileNotFoundError:
            messages.append_error(rf'Cannot locate file \detokenize{{"{input_file}"}}')
            return None
        except PermissionError:
            messages.append_error(rf'Insufficient permission to open file \detokenize{{"{input_file}"}}')
            return None
        except PathSecurityError:
            messages.append_error(rf'Cannot read file in prohibited location: \detokenize{{"{input_file}"}}')
            return None
        hasher = hashlib.md5()
        hasher.update(kpsewhich_input_file_bytes)
        if hasher.hexdigest() != mdfivesum:
            messages.append_error(
                rf'Cannot find the correct input file \detokenize{{"{input_file}"}}; '
                'there may be multiple files with the same name, or the file may have been modified during compilation'
            )
            return None
        code_bytes = kpsewhich_input_file_bytes
    try:
        code = code_bytes.decode(encoding=encoding)
    except UnicodeDecodeError as e:
        messages.append_error(rf'Cannot decode file \detokenize{{"{input_file}"}} with encoding=\detokenize{{"{encoding}"}}')
        return None
    return code




def preprocess_code(code: str, *, messages: Messages,
                    autogobble: bool, gobble: int,
                    rangestartstring: str, rangestartafterstring: str, rangestopstring: str, rangestopbeforestring: str,
                    rangeregex: str, rangeregexmatchnumber: int, rangeregexdotall: bool, rangeregexmultiline: bool) -> str | None:
    if rangeregex and any([rangestartstring, rangestartafterstring, rangestopstring, rangestopbeforestring]):
        messages.append_error('Cannot use "rangeregex" at the same time as range string options')
        return
    if rangestartstring and rangestartafterstring:
        messages.append_error('Cannot use "rangestartstring" and "rangestartafterstring" at the same time')
        return
    if rangestopstring and rangestopbeforestring:
        messages.append_error('Cannot use "rangestopstring" and "rangestopbeforestring" at the same time')
        return

    if rangeregex:
        flags = re.NOFLAG
        if rangeregexdotall:
            flags |= re.DOTALL
        if rangeregexmultiline:
            flags |= re.MULTILINE
        try:
            pattern = re.compile(rangeregex, flags)
        except re.error as e:
            messages.append_error(
                rf'Failed to compile "rangeregex" regular expression (see \detokenize{{{messages.errlog_file_name}}} if it exists)'
            )
            messages.append_errlog(e)
            return
        regex_match: re.Match | None = None
        for n, match_n in enumerate(pattern.finditer(code), start=1):
            if n == rangeregexmatchnumber:
                regex_match = match_n
                break
        if not regex_match:
            messages.append_error('Failed to find match with regular expression "rangeregex"')
            return
        code = regex_match.group()

    if rangestartstring:
        index = code.find(rangestartstring)
        if index == -1:
            messages.append_error('Failed to find string for "rangestartstring"')
            return
        code = code[index:]
    if rangestartafterstring:
        index = code.find(rangestartafterstring)
        if index == -1:
            messages.append_error('Failed to find string for "rangestartafterstring"')
            return
        code = code[index+len(rangestartafterstring):]

    if rangestopstring:
        index = code.find(rangestopstring)
        if index == -1:
            messages.append_error('Failed to find string for "rangestopstring"')
            return
        code = code[:index+len(rangestopstring)]
    if rangestopbeforestring:
        index = code.find(rangestopbeforestring)
        if index == -1:
            messages.append_error('Failed to find string for "rangestopbeforestring"')
            return
        code = code[:index]

    if autogobble:
        code = textwrap.dedent(code)
    if gobble:
        code = ''.join(line[gobble:] or '\n' for line in code.splitlines(True))

    if not code.endswith('\n'):
        code += '\n'

    return code




def highlight(*, md5: str, timestamp: str, messages: Messages, data: dict[str, Any]) -> str | None:
    processed_data = process_highlight_data(messages=messages, data=data)
    if processed_data is None:
        return

    minted_opts, py_opts, code_opts, lexer_opts, filter_opts, formatter_opts = processed_data

    if 'code' in minted_opts:
        code = minted_opts['code']
    else:
        code = load_input_file(messages=messages, input_file=minted_opts['inputfilepath'],
                               mdfivesum=minted_opts['inputfilemdfivesum'], encoding=py_opts['encoding'])
        if code is None:
            return

    code = preprocess_code(code, messages=messages, **code_opts)
    if code is None:
        return

    pygments_lexer: Lexer
    try:
        pygments_lexer = get_lexer_by_name(py_opts['lexer'], **lexer_opts)
    except ClassNotFound:
        if not py_opts['lexer'].endswith('.py') and '.py:' not in py_opts['lexer']:
            messages.append_error(rf'''Pygments lexer \detokenize{{"{py_opts['lexer']}"}} is unknown''')
            return
        try:
            pygments_lexer_class = load_custom_lexer(py_opts['lexer'])
        except (MissingLatexMintedRCError, CustomLexerError, CustomLexerSecurityError) as e:
            messages.append_error(rf'\detokenize{{{str(e)}}}')
            return
        except Exception as e:
            messages.append_error(
                rf'''Failed to load custom lexer \detokenize{{"{py_opts['lexer']}"}}; see \detokenize{{{messages.errlog_file_name}}} if it exists''')
            messages.append_errlog(e)
            return
        pygments_lexer = pygments_lexer_class(**lexer_opts)

    for filter_name in filter_keys_no_options:
        if filter_opts[filter_name]:
            pygments_lexer.add_filter(filter_name)
    for filter_name, opt_name in filter_keys_one_option.items():
        if filter_opts[filter_name]:
            pygments_lexer.add_filter(filter_name, **{opt_name: filter_opts[filter_name]})

    pygments_formatter = LatexFormatter(**formatter_opts)

    highlighted = pygments_highlight(code, pygments_lexer, pygments_formatter)
    highlighted_path = RestrictedPath(data['cachepath']) / minted_opts['highlightfilename']
    try:
        highlighted_path.write_text(highlighted)
    except PermissionError:
        messages.append_error(r'Insufficient permission to write highlighted code')
        return
    except PathSecurityError:
        messages.append_error(
            r'Cannot write highlighted code outside working directory, \detokenize{TEXMFOUTPUT}, and \detokenize{TEXMF_OUTPUT_DIRECTORY}'
        )
        return
    return minted_opts['highlightfilename']
