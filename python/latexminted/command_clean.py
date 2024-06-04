# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from datetime import date, timedelta
from .err import PathSecurityError
from .messages import Messages
from .restricted import cwd_path, json_loads, json_dumps, RestrictedPath, tempfiledir_path, texmfoutput_path




file_roles = ['config', 'data', 'errlog', 'highlight', 'message', 'style']




def clean_messages(*, md5: str):
    paths = [tempfiledir_path]
    if cwd_path is not tempfiledir_path:
        paths.append(cwd_path)
    # Messages and error logs can be written to $TEXMFOUTPUT
    if texmfoutput_path is not None and texmfoutput_path not in paths:
        paths.append(texmfoutput_path)
    for path in paths:
        try:
            (path / f'_{md5}.message.minted').unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass
        try:
            (path / f'_{md5}.errlog.minted').unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass


def clean_temp(*, md5: str):
    paths = [tempfiledir_path]
    if cwd_path is not tempfiledir_path:
        paths.append(cwd_path)
    for path in paths:
        for role in file_roles:
            try:
                (path / f'_{md5}.{role}.minted').unlink(missing_ok=True)
            except (PermissionError, PathSecurityError):
                pass
    # Only messages and error logs can be written to $TEXMFOUTPUT
    if texmfoutput_path is not None and texmfoutput_path not in paths:
        try:
            (texmfoutput_path / f'_{md5}.message.minted').unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass
        try:
            (texmfoutput_path / f'_{md5}.errlog.minted').unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass


def clean_temp_except_errlog(*, md5: str):
    paths = [tempfiledir_path]
    if cwd_path is not tempfiledir_path:
        paths.append(cwd_path)
    for path in paths:
        for role in file_roles:
            if role == 'errlog':
                continue
            try:
                (path / f'_{md5}.{role}.minted').unlink(missing_ok=True)
            except (PermissionError, PathSecurityError):
                pass
    # Only messages and error logs can be written to $TEXMFOUTPUT
    if texmfoutput_path is not None and texmfoutput_path not in paths:
        try:
            (texmfoutput_path / f'_{md5}.message.minted').unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass




def clean(*, md5: str, timestamp: str, messages: Messages, data: dict[str, str],
          additional_cache_file_names: list[str] | None = None):
    clean_temp_except_errlog(md5=md5)

    # Python < 3.11 requires `YYYY-MM-DD`
    timestamp_date = date.fromisoformat(f'{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}')
    cache_path = RestrictedPath(data['cachepath'])
    current_index_name = f'_{md5}.index.minted'
    used_cache_files: set[str] = set()
    used_cache_files.add(current_index_name)
    if additional_cache_file_names is not None:
        used_cache_files.update(additional_cache_file_names)
    used_cache_files.update(data['cachefiles'])


    for index_path in cache_path.glob('*.index.minted'):
        if index_path.name == current_index_name:
            continue

        try:
            index_data = json_loads(index_path.read_bytes())
        except PathSecurityError:
            messages.append_error(
                rf'Cannot read file \detokenize{{"{index_path.name}"}} outside working directory, \detokenize{{TEXMFOUTPUT}}, and \detokenize{{TEXMF_OUTPUT_DIRECTORY}}'
            )
            continue
        except PermissionError:
            messages.append_error(rf'Insufficient permission to open file \detokenize{{"{index_path.name}"}}')
            continue

        # Python < 3.11 requires `YYYY-MM-DD`
        index_data_ts = index_data['timestamp']
        index_date = date.fromisoformat(f'{index_data_ts[:4]}-{index_data_ts[4:6]}-{index_data_ts[6:8]}')
        index_age = timestamp_date - index_date
        if index_age > timedelta(days=30):
            # Delete index files more than 30 days old
            try:
                index_path.unlink(missing_ok=True)
            except PathSecurityError:
                messages.append_error(
                    rf'Cannot delete file \detokenize{{"{index_data.name}"}} outside working directory, \detokenize{{TEXMFOUTPUT}}, and \detokenize{{TEXMF_OUTPUT_DIRECTORY}}'
                )
            except PermissionError:
                messages.append_error(rf'Insufficient permission to delete outdated cache file \detokenize{{"{index_path.name}"}}')
            continue

        used_cache_files.add(index_path.name)
        used_cache_files.update(index_data['cachefiles'])

    for minted_path in cache_path.glob('*.minted'):
        if minted_path.name not in used_cache_files:
            try:
                minted_path.unlink(missing_ok=True)
            except PathSecurityError:
                messages.append_error(
                    rf'Cannot delete file \detokenize{{"{minted_path.name}"}} outside working directory, \detokenize{{TEXMFOUTPUT}}, and \detokenize{{TEXMF_OUTPUT_DIRECTORY}}'
                )
            except PermissionError:
                messages.append_error(rf'Insufficient permission to delete unused cache file \detokenize{{"{minted_path.name}"}}')

    new_index_data = {
        'jobname': data['jobname'],
        'md5': md5,
        'timestamp': timestamp,
        'cachefiles': sorted(used_cache_files),
    }
    new_index_path = cache_path / current_index_name
    try:
        new_index_path.write_text(json_dumps(new_index_data, indent=2))
    except PathSecurityError:
        messages.append_error(
            rf'Cannot write file \detokenize{{"{new_index_path.name}"}} outside working directory, \detokenize{{TEXMFOUTPUT}}, and \detokenize{{TEXMF_OUTPUT_DIRECTORY}}'
        )
    except PermissionError:
        messages.append_error(rf'Insufficient permission to write file \detokenize{{"{new_index_path.name}"}}')
