# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations




class LatexMintedError(Exception):
    pass

class LatexMintedConfigError(LatexMintedError):
    pass

class CustomLexerError(LatexMintedError):
    pass
