# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from os import environ as os_environ
# ruff: noqa: E402
os_environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
import argparse
import sys
from latex2pydata import __version__ as latex2pydata_version
from pygments import __version__ as pygments_version
from .version import __version__




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

    # Lazy imports for functions that are designed to work only within LaTeX
    # shell escape.  These require SELFAUTOLOC and/or TEXSYSTEM environment
    # variables, which are set by LaTeX.  Without the lazy import, these can
    # raise errors and prevent `--help` etc. from functioning when `main()` is
    # not running within LaTeX shell escape.
    def batch(**kwargs):
        from .command_batch import batch
        batch(**kwargs)

    def clean(**kwargs):
        from .command_clean import clean
        clean(**kwargs)

    def clean_config(**kwargs):
        from .command_clean import clean_config_temp
        clean_config_temp(**kwargs)

    def clean_temp(**kwargs):
        from .command_clean import clean_temp_except_errlog
        clean_temp_except_errlog(**kwargs)

    def config(**kwargs):
        from .command_config import config
        config(**kwargs)

    def highlight(**kwargs):
        from .command_highlight import highlight
        highlight(**kwargs)

    def styledef(**kwargs):
        from .command_styledef import styledef
        styledef(**kwargs)

    parser_batch = subparsers.add_parser('batch', help='Batch process highlight, styledef, and clean')
    parser_batch.set_defaults(func=batch)
    parser_batch.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_batch.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_batch.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_clean = subparsers.add_parser('clean', help='Clean up temp files and unused cache files')
    parser_clean.set_defaults(func=clean)
    parser_clean.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_clean.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_clean.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_cleanconfig = subparsers.add_parser('cleanconfig', help='Clean up config temp file')
    parser_cleanconfig.set_defaults(func=clean_config)
    parser_cleanconfig.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_cleanconfig.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_cleanconfig.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_cleantemp = subparsers.add_parser('cleantemp', help='Clean up temp files')
    parser_cleantemp.set_defaults(func=clean_temp)
    parser_cleantemp.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_cleantemp.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_cleantemp.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_config = subparsers.add_parser('config', help='Detect configuration and save it to file for \\input')
    parser_config.set_defaults(func=config)
    parser_config.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_config.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_config.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_highlight = subparsers.add_parser('highlight', help='Highlight code and save it to file for \\input')
    parser_highlight.set_defaults(func=highlight)
    parser_highlight.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_highlight.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_highlight.add_argument('md5', help=r'MD5 hash based on \jobname')

    parser_styledef = subparsers.add_parser('styledef', help='Generate highlighting style definition and save it to file for \\input')
    parser_styledef.set_defaults(func=styledef)
    parser_styledef.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
    parser_styledef.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
    parser_styledef.add_argument('md5', help=r'MD5 hash based on \jobname')

    cmdline_args = parser.parse_args()

    func_keys = set(['md5', 'timestamp', 'debug'])
    func_args = {k: v for k, v in vars(cmdline_args).items() if k in func_keys}
    if cmdline_args.subparser_name in ('cleanconfig', 'cleantemp'):
        # Some functions don't need all arguments
        func_args.pop('debug')
        func_args.pop('timestamp')
    md5: str | None = func_args.get('md5')
    timestamp: str | None = func_args.get('timestamp')
    if md5 is None or timestamp is None:
        cmdline_args.func(**func_args)
        sys.exit()

    from .command_clean import clean_messages, paths_skipped_in_initial_temp_cleaning
    from .debug import debug_mv_data
    from .err import LatexMintedConfigError
    from .load_data import load_data
    from .messages import Messages

    clean_messages(md5=md5)
    messages = Messages(md5=md5)
    func_args['messages'] = messages
    try:
        maybe_data = load_data(md5=md5, messages=messages, timestamp=timestamp, command=cmdline_args.subparser_name)
    except LatexMintedConfigError as e:
        messages.append_error(
            f'Failed to load latexminted configuration:  {e}'
        )
        messages.communicate()
        sys.exit(1)
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
    if maybe_data is None:
        messages.append_error('Unexpectedly received no data without any error messages')
        messages.communicate()
        sys.exit(1)

    data, data_path = maybe_data
    func_args['data'] = data
    debug: bool = func_args.get('debug', False)
    if debug:
        paths_skipped_in_initial_temp_cleaning.add(data_path)
    cmdline_args.func(**func_args)
    if debug:
        debug_mv_data(md5=md5, data_path=data_path)
    messages.communicate()
    if messages.has_errors():
        sys.exit(1)
