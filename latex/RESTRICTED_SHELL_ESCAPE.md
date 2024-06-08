# Restricted Shell Escape Security — minted LaTeX package

The `minted` LaTeX package is designed to be compatible with the security
requirements for LaTeX restricted shell escape.  This document summarizes the
steps that are taken for security compliance in the LaTeX package and the
accompanying Python executable.  There is a corresponding file in the
`latexminted` Python package that summarizes security on the Python side.

LaTeX can run arbitrary shell commands while compiling documents, but this is
typically disabled for security reasons.  Enabling arbitrary shell commands
requires running LaTeX with `-shell-escape` or a similar command-line option,
or modifying LaTeX configuration.  `minted` versions 1 and 2 required
`-shell-escape`, which allowed running the `pygmentize` executable to
highlight code but also allowed for arbitrary code execution.  `minted`
version 3 uses new Python executables that are part of the `minted` LaTeX
package and the `latexminted` Python package.  These executable are designed
to be accepted as trusted programs that TeX distributions allow to run by
default, without needing `-shell-escape`.  This is referred to as "restricted
shell scape," shell escape but only for trusted executables.


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


## `latexminted` executable

The LaTeX package includes a Python executable called `latexminted` that is
intended for installation within TeX distributions.  Because the `latexminted`
executable has significant security implications, it is in a separate
`restricted/` directory in this repository, so that it is easier to see
whether commits modify any code with security implications.

The executable typically imports and then runs the `main()` function from the
`latexminted` Python package.  This involves no additional security
implications beyond the `latexminted` Python package itself.

Depending on system configuration, the `latexminted` executable may launch a
subprocess instead.

1.  The libraries used by the `latexminted` executable require Python >= 3.8.
    If the default Python version is < 3.8, then `latexminted` will attempt to
    locate a more recent Python installation and run itself with that Python
    version in a subprocess.  Python's `shutil.which()` is used to search
    `PATH` for more recent Python versions.

2.  When the `minted` LaTeX package is installed, the `latexminted` Python
    package and all other required Python libraries including Pygments are
    also installed within the TeX distribution in the form of Python wheels
    `*.whl`.  It is also possible to install the `latexminted` Python package
    and Pygments separately, within a Python installation.  This is necessary
    to use plugin packages for Pygments.  If the `latexminted` Python package
    is installed within a Python installation, then it will create a
    `latexminted` executable within that Python installation.

    When the `latexminted` executable that is installed within a TeX
    distribution runs, it checks for the existence of a `latexminted`
    executable within a Python installation.  If that executable exists and
    has a higher precedence on `PATH`, then that executable runs in a
    subprocess.  Python's `shutil.which()` is used to search `PATH` for
    `latexminted` executables outside the TeX distribution.

Whenever a subprocess is used to run an executable, that executable must meet
two conditions:

  * The executable must exist on `PATH`, outside the current working directory
    or a subdirectory and outside `TEXMFOUTPUT` and `TEXMF_OUTPUT_DIRECTORY`.

  * The current directory, `TEXMFOUTPUT`, and `TEXMF_OUTPUT_DIRECTORY` cannot
    be subdirectories of the directory in which the executable is located.
