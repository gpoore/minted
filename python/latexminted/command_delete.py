# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

from .err import PathSecurityError
from .restricted import cwd_path, tempfiledir_path




def delete(*, file: str):
    paths = [tempfiledir_path]
    if cwd_path is not tempfiledir_path:
        paths.append(cwd_path)
    for path in paths:
        try:
            (path / file).unlink(missing_ok=True)
        except (PermissionError, PathSecurityError):
            pass
