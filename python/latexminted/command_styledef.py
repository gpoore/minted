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
from pygments.formatters import LatexFormatter
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound
from .messages import Messages
from .restricted import MintedTempRestrictedPath




def styledef(*, md5: str, timestamp: str, debug: bool, messages: Messages, data: dict[str, str]) -> str | None:
    style = data['style']
    try:
        StyleClass = get_style_by_name(style)
    except ClassNotFound:
        messages.append_error(rf'Pygments style \detokenize{{"{style}"}} was not found')
        return

    style_defs = LatexFormatter(style=StyleClass, commandprefix=data['commandprefix']).get_style_defs().lstrip()
    styledef_path = MintedTempRestrictedPath(data['cachepath']) / data['styledeffilename']
    try:
        styledef_path.parent.mkdir(parents=True, exist_ok=True)
        styledef_path.write_text(style_defs, encoding='utf8')
    except PermissionError:
        messages.append_error(rf'Insufficient permission to write style file for \detokenize{{"{style}"}}')
        return
    except PathSecurityError:
        messages.append_error(
            rf'Cannot write \detokenize{{"{style}"}} style file outside working directory, \detokenize{{TEXMFOUTPUT}}, and \detokenize{{TEXMF_OUTPUT_DIRECTORY}}'
        )
        return
    return data['styledeffilename']
