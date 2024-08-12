# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from latexrestricted import PathSecurityError
from .restricted import MintedTempRestrictedPath




def debug_mv_data(*, md5, data_path: MintedTempRestrictedPath) -> MintedTempRestrictedPath | None:
    for n in range(1, 101):
        replacement_path = data_path.parent / f'_{md5}_{n}.data.minted'
        if not replacement_path.is_file():
            break
    else:
        return None
    try:
        data_path.replace(replacement_path)
    except (FileNotFoundError, PermissionError, PathSecurityError):
        return None
    return replacement_path
