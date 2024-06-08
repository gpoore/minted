# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from .restricted import os_environ
# ruff: noqa: E402
os_environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
import argparse
import sys
from latex2pydata import __version__ as latex2pydata_version
from pygments import __version__ as pygments_version
from .version import __version__
from .command_batch import batch
from .command_clean import clean, clean_messages
from .command_config import config
from .command_delete import delete
from .command_highlight import highlight
from .command_styledef import styledef
from .load_data import load_data
from .messages import Messages




def main():
    parser = argparse.ArgumentParser(prog='latexminted', allow_abbrev=False)
    parser.set_defaults(func=lambda **x: parser.print_help())
    library_version = ', '.join([
        f'latex2pydata {latex2pydata_version}',
        f'pygments {pygments_version}'
    ])
    version = f'latexminted {__version__} (libraries: {library_version})'
    parser.add_argument('--version', action='version', version=version)
    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_batch = subparsers.add_parser('batch', help='Batch process highlight, styledef, and clean')
    parser_batch.set_defaults(func=batch)
    parser_batch.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_batch.add_argument('md5', help=r'MD5 hash based \jobname')

    parser_clean = subparsers.add_parser('clean', help='Clean up temp files and unused cache files')
    parser_clean.set_defaults(func=clean)
    parser_clean.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_clean.add_argument('md5', help=r'MD5 hash based \jobname')

    parser_config = subparsers.add_parser('config', help='Detect configuration and save it to file for \\input')
    parser_config.set_defaults(func=config)
    parser_config.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_config.add_argument('md5', help=r'MD5 hash based \jobname')

    parser_delete = subparsers.add_parser('delete', help='Delete file (restricted filenames only)')
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument('file', help='File to delete')

    parser_highlight = subparsers.add_parser('highlight', help='Highlight code and save it to file for \\input')
    parser_highlight.set_defaults(func=highlight)
    parser_highlight.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_highlight.add_argument('md5', help=r'MD5 hash based \jobname')

    parser_styledef = subparsers.add_parser('styledef', help='Generate highlighting style definition and save it to file for \\input')
    parser_styledef.set_defaults(func=styledef)
    parser_styledef.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_styledef.add_argument('md5', help=r'MD5 hash based \jobname')

    cmdline_args = parser.parse_args()

    func_keys = set(['md5', 'file', 'timestamp'])
    func_args = {k: v for k, v in vars(cmdline_args).items() if k in func_keys}
    md5: str | None = func_args.get('md5')
    timestamp: str | None = func_args.get('timestamp')
    if md5 is None or timestamp is None:
        cmdline_args.func(**func_args)
        sys.exit()

    clean_messages(md5=md5)
    messages = Messages(md5=md5)
    func_args['messages'] = messages
    try:
        data = load_data(md5=md5, messages=messages, timestamp=timestamp, command=cmdline_args.subparser_name)
    except Exception as e:
        messages.append_error(
            rf'Failed due to unexpected error (see \detokenize{{"{messages.errlog_file_name}"}} if it exists)'
        )
        messages.append_errlog(e)
        messages.communicate()
        sys.exit(1)

    if messages.data_file_not_found and cmdline_args.subparser_name == 'config':
        config(**func_args)
        sys.exit(1)
    if messages.has_errors():
        messages.communicate()
        sys.exit(1)
    if data is None:
        messages.append_error('Unexpectedly received no data without any error messages')
        messages.communicate()
        sys.exit(1)

    func_args['data'] = data
    cmdline_args.func(**func_args)
    messages.communicate()
    if messages.has_errors():
        sys.exit(1)
