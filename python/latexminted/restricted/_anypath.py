# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the LaTeX Project Public License version 1.3c:
# https://www.latex-project.org/lppl.txt
#


from __future__ import annotations

import pathlib
import sys
try:
    from typing import Self
except ImportError:
    pass




# The `type(...)` is needed to inherit the `_flavour` attribute
class AnyPath(type(pathlib.Path())):
    if sys.version_info[:2] < (3, 9):
        def is_relative_to(self, other: AnyPath) -> bool:
            try:
                self.relative_to(other)
            except ValueError:
                return False
            return True


    # `super().resolve()` may be used frequently in determining whether paths
    # are readable/writable/executable.  `.resolve()` and `.parent()` cache
    # and track resolved paths to minimize file system access.
    _resolved_set: set[tuple[type[Self], Self]] = set()
    _resolve_cache: dict[tuple[type[Self], Self], Self] = {}

    def resolve(self) -> Self:
        key = (type(self), self)
        try:
            resolved = self._resolve_cache[key]
        except KeyError:
            resolved = super().resolve()
            resolved_key = (key[0], resolved)
            self._resolved_set.add(resolved_key)
            self._resolve_cache[key] = resolved
            self._resolve_cache[resolved_key] = resolved
        return resolved

    @property
    def parent(self) -> Self:
        parent = super().parent
        key = (type(self), self)
        if key in self._resolved_set:
            parent_key = (key[0], parent)
            self._resolved_set.add(parent_key)
            self._resolve_cache[parent_key] = parent
        return parent
