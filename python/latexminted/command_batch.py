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
from .command_styledef import styledef
from .command_highlight import highlight
from .command_clean import clean
from .messages import Messages




def batch(*, md5: str, timestamp: str, messages: Messages, data: list[dict[str, Any]]):
    new_cache_file_names: list[str] = []
    for d in data:
        command = d['command']
        if command == 'styledef':
            messages.set_context(d)
            f = styledef(md5=md5, timestamp=timestamp, messages=messages, data=d)
            if f is not None:
                new_cache_file_names.append(f)
        elif command == 'highlight':
            messages.set_context(d)
            f = highlight(md5=md5, timestamp=timestamp, messages=messages, data=d)
            if f is not None:
                new_cache_file_names.append(f)
        elif command == 'clean':
            messages.set_context()
            # Don't need to check whether clean is at the end of the list of
            # commands, since the LaTeX side disables the Python executable
            # immediately after clean.
            clean(md5=md5, timestamp=timestamp, messages=messages, data=d, additional_cache_file_names=new_cache_file_names)
        else:
            raise ValueError

    if data and data[-1]['command'] != 'clean':
        messages.set_context()
        # Batch mode is a special case for clean.  When a document without an
        # existing cache is first compiled, an explicit clean command is not
        # written to the data file because there are no cache files in use
        # since they don't yet exist.  However, at the end of the batch, these
        # files do exist, so clean should be invoked to create an index.
        clean_data = {
            'jobname': data[-1]['jobname'],
            'cachepath': data[-1]['cachepath'],
            'cachefiles': [],
        }
        clean(md5=md5, timestamp=timestamp, messages=messages, data=clean_data, additional_cache_file_names=new_cache_file_names)
