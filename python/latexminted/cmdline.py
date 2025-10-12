# -*- coding: utf-8 -*-
#
# Copyright (c) 2024-2025, Geoffrey M. Poore
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
import shutil
import sys
import textwrap
from typing import Callable



class ArgParser(argparse.ArgumentParser):
    def __init__(self, *, prog: str, **kwargs):
        super().__init__(
            prog=prog,
            allow_abbrev=False,
            formatter_class=argparse.RawTextHelpFormatter,
            **kwargs
        )
        self._prog = prog
        self._command_subparsers = None
        self._command_help_dict = None

    def add_command(self, name: str, *, help: str, func: Callable[..., None]):
        if self._command_subparsers is None:
            self._command_subparsers = self.add_subparsers(dest='subparser_name')
        if self._command_help_dict is None:
            self._command_help_dict = {}
        self._command_help_dict[name] = help
        parser = self._command_subparsers.add_parser(name, help=help)
        parser.set_defaults(func=func)
        parser.add_argument('--timestamp', help='LaTeX compile timestamp', required=True)
        parser.add_argument('--debug', help='Keep temp files for debugging', action='store_true')
        parser.add_argument('md5', help=r'MD5 hash based on \jobname')

    def print_help(self):
        term_columns = shutil.get_terminal_size()[0]
        help_lines = []
        if self._command_help_dict:
            help_lines.append(f'usage: {self._prog} [-h] [--version] COMMAND [--debug] --timestamp TIME MD5')
        else:
            help_lines.append(f'usage: {self._prog} [-h] [--debug] --timestamp TIME MD5')
        help_lines.extend([
            '',
            'Python executable for the LaTeX minted package.',
            r'Designed to be launched from within LaTeX via \ShellEscape.',
            '',
            'positional arguments:',
        ])
        if self._command_help_dict:
            command_choices = ', '.join(k for k in sorted(self._command_help_dict))
            if len(command_choices) - 14 - 2 > term_columns:
                command_choices = ','.join(k for k in sorted(self._command_help_dict))
            help_lines.append(f'  {"COMMAND":<12}{{{command_choices}}}')
            for k, v in sorted(self._command_help_dict.items()):
                help_lines.append(
                    textwrap.fill(f'{" "*16}* {k}: {v}', subsequent_indent=' '*16, width=term_columns)
                )
        help_lines.extend([
           r'  MD5         MD5 hash of LaTeX \jobname',
            '  TIME        LaTeX compilation timestamp (YYYYDDMMHHMMSS)',
            '',
            'options:',
            '  --debug     Keep temp files for debugging',
            '  -h, --help  Show this help message and exit',
            "  --version   Show program's version number and exit\n" if self._command_help_dict else '',
            'Repository: https://github.com/gpoore/minted',
            'CTAN: https://ctan.org/pkg/minted',
            'PyPI: https://pypi.org/project/latexminted',
        ])
        print('\n'.join(help_lines), file=sys.stdout)




def main():
    parser = ArgParser(
        prog='latexminted',
    )
    parser.set_defaults(func=lambda **x: parser.print_help())


    def get_version():
        from .version import __version__
        from latex2pydata import __version__ as latex2pydata_version
        from latexrestricted import __version__ as latexrestricted_version
        from pygments import __version__ as pygments_version
        library_versions = ', '.join([
            f'latex2pydata {latex2pydata_version}',
            f'latexrestricted {latexrestricted_version}',
            f'pygments {pygments_version}',
        ])
        return '\n'.join([
            f'latexminted {__version__}',
            'Python executable for the LaTeX minted package',
            f'Libraries: {library_versions}',
            'Repository: https://github.com/gpoore/minted',
            'CTAN: https://ctan.org/pkg/minted',
            'PyPI: https://pypi.org/project/latexminted',
        ])

    parser.add_argument('--version', action='version', version=get_version())

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

    parser.add_command('batch', help='Batch process highlight, styledef, and clean', func=batch)
    parser.add_command('clean', help='Clean up temp files and unused cache files', func=clean)
    parser.add_command('cleanconfig', help='Clean up config temp file', func=clean_config)
    parser.add_command('cleantemp', help='Clean up temp files', func=clean_temp)
    parser.add_command('config', help='Detect configuration and save it to file', func=config)
    parser.add_command('highlight', help='Highlight code and save it to file', func=highlight)
    parser.add_command(
        'styledef', help='Generate highlighting style definition and save it to file', func=styledef
    )

    cmdline_args = parser.parse_args()

    func_keys = set(['md5', 'timestamp', 'debug'])
    func_args = {k: v for k, v in vars(cmdline_args).items() if k in func_keys}
    if cmdline_args.subparser_name in ('cleanconfig', 'cleantemp'):
        # Some functions don't need all arguments
        func_args.pop('timestamp')
    md5: str | None = func_args.get('md5')
    timestamp: str | None = func_args.get('timestamp')
    if md5 is None or timestamp is None:
        cmdline_args.func(**func_args)
        sys.exit()

    from .command_clean import clean_messages, paths_skipped_in_initial_temp_cleaning
    from .debug import debug_mv_data
    from .load_data import load_data
    from .messages import Messages
    from .restricted import latexminted_config
    clean_messages(md5=md5)
    messages = Messages(md5=md5)
    func_args['messages'] = messages

    # All commands but `config` must exit immediately in the event of errors.
    # `config` must proceed as far as possible.   The `config()` function must
    # run, since its output is used on the LaTeX side in determining whether
    # the `latexminted` executable can be located.  Note that `config()` is
    # designed to handle the possibility of missing data.

    if latexminted_config.config_error and cmdline_args.subparser_name != 'config':
        messages.append_error(
            f'Failed to load latexminted configuration:  {latexminted_config.config_error}'
        )
        messages.communicate()
        sys.exit(1)

    try:
        maybe_data = load_data(md5=md5, messages=messages, timestamp=timestamp, command=cmdline_args.subparser_name)
    except Exception as e:
        messages.append_error(
            rf'Failed due to unexpected error (see \detokenize{{"{messages.errlog_file_name}"}} if it exists)'
        )
        messages.append_errlog(e)
        if cmdline_args.subparser_name == 'config':
            if latexminted_config.config_error:
                messages.append_error(
                    f'Failed to load latexminted configuration:  {latexminted_config.config_error}'
                )
            config(**func_args)
        messages.communicate()
        sys.exit(1)

    if messages.has_errors():
        if cmdline_args.subparser_name == 'config':
            if latexminted_config.config_error:
                messages.append_error(
                    f'Failed to load latexminted configuration:  {latexminted_config.config_error}'
                )
            config(**func_args)
        messages.communicate()
        sys.exit(1)
    if maybe_data is None:
        messages.append_error('Unexpectedly received no data without any error messages')
        if cmdline_args.subparser_name == 'config':
            if latexminted_config.config_error:
                messages.append_error(
                    f'Failed to load latexminted configuration:  {latexminted_config.config_error}'
                )
            config(**func_args)
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
