# Restricted Shell Escape Security — minted LaTeX package

The `minted` LaTeX package is designed to be compatible with the security
requirements for LaTeX restricted shell escape.  This document summarizes the
steps that are taken for security compliance in the LaTeX package.  There is a
corresponding file in the `latexminted` Python package that summarizes
security on the Python side.

LaTeX can run arbitrary shell commands while compiling documents, but this is
typically disabled for security reasons.  Enabling arbitrary shell commands
requires running LaTeX with `-shell-escape` or a similar command-line option,
or modifying LaTeX configuration.  `minted` versions 1 and 2 required
`-shell-escape`, which allowed running the `pygmentize` executable to
highlight code but also allowed for arbitrary code execution.  `minted`
version 3 uses a new Python executable that is part of the `latexminted`
Python package.  This executable is designed to be accepted as one of the
trusted programs that TeX distributions allow to run by default, without
needing `-shell-escape`.  This is referred to as "restricted shell scape,"
shell escape but only for trusted executables.


## `minted.sty` LaTeX style file

In `minted.sty`, the `latexminted` Python executable is invoked via
`\ShellEscape`.  There are only three types of options that are ever passed to
the executable:

 *  Timestamps (`--timestamp <digits>`).  These involve only digits, so no
    quoting or escaping is needed.

 *  MD5 hashes.  These involve only hexadecimal digits, that is,
    `[0-9a-fA-F]`, so no quoting or escaping is needed.

 *  File names.  These are only for a restricted set of temp files, of the
    form `_<MD5-hash>.<role>.minted`, where `<role>` consists only of ASCII
    alphabetical characters and describes the role of the temp file (for
    example, `data` or `config`).  Again, no quoting or escaping is needed.

In summary, all usage of `\ShellEscape` involves commands that require no
quoting or escaping.  TeX Live quotes and escapes commands that are used with
restricted shell escape (for example,
https://github.com/TeX-Live/texlive-source/blob/e47512fcb293e2390b609bce612449d579efc230/texk/web2c/doc/web2c.info#L1573).
But even if this were not the case, all commands would be safe.

The LaTeX package sends data to the `latexminted` Python executable by
writing data to temp files, using Python literal syntax (see the
[latex2pydata](https://github.com/gpoore/latex2pydata) LaTeX and Python
packages).  This is done using standard `\openout` and `\write`, so LaTeX
controls which locations are writable and there are no additional security
implications.

The `latexminted` Python executable sends data to the LaTeX package by
writing temp files or cache files.  These are brought into the LaTeX document
using standard `\input`, `\InputIfFileExists`, etc., so LaTeX controls which
files are readable and there are no additional security implications.

Overall, then, the `minted.sty` part of the LaTeX package has no security
implications that are different from any other package that can write or read
files, except for running the `latexminted` Python executable.


## `latexmintedwin` executable

Under Windows with restricted shell escape, TeX Live interprets executables without a full path as being executables within the TeX Live `bin/windows/` directory.

 *  Relevant changelog:
    https://github.com/TeX-Live/texlive-source/blob/e47512fcb293e2390b609bce612449d579efc230/texk/web2c/lib/ChangeLog#L820

 *  Implementation:
    https://github.com/TeX-Live/texlive-source/blob/e47512fcb293e2390b609bce612449d579efc230/texk/web2c/lib/texmfmp.c#L534

Otherwise, Windows could run an executable with the same name that is located
in the current working directory, which is typically writable by LaTeX.  As a
byproduct, this effectively limits restricted shell escape executables to
those within the TeX Live `bin/windows/` directory.

To work within these constraints, the `minted` LaTeX package includes a Python
executable `latexmintedwin` that is intended for installation within TeX
distributions.  `latexmintedwin` is separate from the `latexminted` Python
package and its executable, which are intended for installation as part of a
Python distribution outside of LaTeX.

In TeX Live, an executable wrapper `latexmintedwin.exe` is created in
`bin/windows/` by creating a copy of `runscript.exe` and then renaming it to
`latexmintedwin.exe`.  Then the file `latexmintedwin.py` is placed in
`texmf-dist/scripts/minted`.  When `latexmintedwin.exe` runs, it will
automatically locate and invoke `latexmintedwin.py`.

`latexmintedwin` can run in two separate modes:

1.  The current default Python installation is used by `runscript.exe` to
    execute `latexmintedwin.py`.  If this Python installation has the
    `latexminted` Python library installed, then the `main()` function is
    imported from this library and executed.  In this case, there are no
    security implications beyond those in the `latexminted` Python library
    itself.

2.  If the current default Python installation does not have the
    `latexminted` Python library, then `latexmintedwin.py` looks for
    `latexminted.exe` on PATH.  It is possible that `latexminted` is
    installed elsewhere, in a different Python installation.  If
    `latexminted.exe` is found, outside of all locations writable by LaTeX
    and within a Python installation, then it is executed in a subprocess.
    See `latexmintedwin.py` for the full details of safely locating and
    running `latexminted.exe`.

Unlike the `minted.sty` part of the package that essentially inherits security
from LaTeX, `latexmintedwin` has significant security implications.  As a
result, it is in a separate `restricted/` directory in this repository, so
that it is easier to see whether commits modify any code with security
implications.
