# Restricted Shell Escape Security — `latexminted` Python package

The `latexminted` Python package is designed to be compatible with the
security requirements for LaTeX restricted shell escape.  This document
summarizes the steps that are taken for security compliance in the Python
package.  There is a corresponding file in the `minted` LaTeX package that
summarizes security on the LaTeX side.

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


## `latexminted` and the file system

Restricted access to the file system is one aspect of the requirements for
restricted shell escape.  File system access depends on LaTeX configuration,
which is accessed via the
[`latexrestricted` Python package](https://github.com/gpoore/latexrestricted/).
TeX Live restrictions depend on `openin_any` and `openout_any` settings in
[`texmf.cnf`](https://tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/texmf.cnf?revision=70942&view=markup#l684).
MiKTeX restrictions depend on `[Core]AllowUnsafeInputFiles` and
`[Core]AllowUnsafeOutputFiles` in
[`miktex.ini`](https://docs.miktex.org/manual/miktex.ini.html).
The default restrictions may be summarized as follows:

  * Reading:  No restrictions.

  * Writing:  Prohibit writing dotfiles.  Restrict writing to locations under
    the current working directory, `TEXMFOUTPUT`, and
    `TEXMF_OUTPUT_DIRECTORY`.

Python provides a number of ways to read and write files, including the
[`open()`](https://docs.python.org/3/library/functions.html#open) function,
the [`io`](https://docs.python.org/3/library/io.html) module, and the
[`pathlib`](https://docs.python.org/3/library/pathlib.html) module.  The
`latexminted` library restricts access to the file system as follows.

1.  All security-related functionality, including file system access, is
    provided through the `restricted` subpackage, which partially depends on
    the separate
    [`latexrestricted` package](https://github.com/gpoore/latexrestricted/).
    This makes it easier to see whether commits modify any code with security
    implications.

2.  Within the `restricted` subpackage, there are `RestrictedPath` subclasses
    of `pathlib.Path`.  All file path objects that are created in response to
    user data from LaTeX are instances of these `RestrictedPath` classes.
    File system operations are initiated using instances of `RestrictedPath`
    classes, including creating directories and reading and writing files.

    By default, `MintedResolvedRestrictedPath` is used for all paths.  This is
    a subclass of `SafeWriteResolvedRestrictedPath` from the `latexrestricted`
    package.  Paths are checked against the file system and symlinks are
    resolved before comparing paths with permitted read/write locations.
    Security settings for reading are inherited from LaTeX settings.  Security
    settings for writing are always set at maximum:  no writing dotfiles, and
    no writing outside the current working directory, `TEXMFOUTPUT`, and
    `TEXMF_OUTPUT_DIRECTORY`.  See the documentation of the `latexrestricted`
    package for implementation details.

    The `security.file_path_analysis` setting from `.minted_config` defaults
    to `resolve`, but if it is set to `string` instead, then
    `MintedStringRestrictedPath` is used instead of
    `MintedResolvedRestrictedPath`.  This is a subclass of
    `SafeWriteStringRestrictedPath` from the `latexrestricted` package.
    Instead of resolving paths with the file system and then comparing them
    against permitted read/write locations, it performs all path analysis by
    treating paths as strings.  This follows the TeX file path security
    implementation, and as a byproduct places limits on valid paths while
    making it possible to circumvent security settings via symlinks.  All
    relative paths must be relative to the current working directory.  All
    absolute paths must be under `TEXMFOUTPUT` and `TEXMF_OUTPUT_DIRECTORY`.
    Paths cannot contain `..` to access parent directories, even if those
    locations are permitted for reading/writing.  Because paths are only
    analyzed as strings, it is possible to access locations outside the
    current working directory, `TEXMFOUTPUT`, and `TEXMF_OUTPUT_DIRECTORY` via
    symlinks in those locations.  See the documentation of the
    `latexrestricted` package for implementation details.

    Regardless of whether paths are resolved with the file system or analyzed
    as strings, writing/deleting files is further restricted to file names
    matching this regular expression:
    ```
    [0-9a-zA-Z_-]+\.(?:config|data|errlog|highlight|index|message|style)\.minted
    ```
    All temp files and cache files created by the `minted` LaTeX package and
    the `latexminted` executable match this regular expression.

3.  Some modules and packages such as `json`, `tomllib`, and `latex2pydata`
    provide functions for loading data from files and also functions for
    loading it from strings or bytes.  Only the functions for loading data
    from strings or bytes are imported from these modules and packages; the
    full modules and packages are not imported.  For example, `import json` is
    replaced by `from json import loads as json_loads`.  This reduces the
    danger of thoughtlessly trying to use `json.load()` and then carelessly
    using `open()` instead of `RestrictedPath`.


## `latexminted` and subprocesses

It can be necessary in some cases to run external commands.  Currently, this
is limited to using `kpsewhich` and `initexmf` to access LaTeX configuration,
and using `kpsewhich` to locate files.  The `LatexConfig` class from the
[`latexrestricted` package](https://github.com/gpoore/latexrestricted/) is
used for these tasks.  It takes the following steps to ensure safe subprocess
access.

1.  The executable is restricted to `kpsewhich` and `initexmf`.

2.  The executable must exist on `PATH`, as found by
    [`shutil.which()`](https://docs.python.org/3/library/shutil.html#shutil.which),
    or at a location specified with the environment variable `SELFAUTOLOC`,
    which is set by TeX Live.  The executable must not be in a location
    writable by LaTeX.  For added security, locations writable by LaTeX cannot
    be under the executable parent directory.

3.  The executable cannot be a batch file (no `*.bat` or `*.cmd`), to prevent
    the command from
    [running in a system shell under Windows](https://docs.python.org/3/library/subprocess.html#security-considerations).

4.  The subprocess must run with `shell=False`.  That is, the executable is
    called directly, not through a system shell, so quoting and escaping to
    avoid shell injection is not needed since there is no shell.
