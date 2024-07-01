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
restricted shell escape.  The default restrictions may be summarized as
follows, based on the TeX Live configuration file
[`texmf.cnf`](https://tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/texmf.cnf?revision=70942&view=markup#l634)
plus the changelog for `kpathsea` which mentions the new environment variable
[`TEXMF_OUTPUT_DIRECTORY`](https://www.tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/NEWS?view=markup).

  * Reading:  No restrictions.

  * Writing:  Prohibit writing dotfiles.  Restrict writing to the current
    working directory, `TEXMFOUTPUT`, and `TEXMF_OUTPUT_DIRECTORY`, plus their
    subdirectories.

The exact way that these restrictions are described in the TeX Live sources is
somewhat different (for example, disallowing going to parent directories), but
this is the overall effect of the restrictions.

Python provides a number of ways to read and write files, including the
[`open()`](https://docs.python.org/3/library/functions.html#open) function,
the [`io`](https://docs.python.org/3/library/io.html) module, and the
[`pathlib`](https://docs.python.org/3/library/pathlib.html) module.  The
`latexminted` library restricts access to the file system as follows.

1.  All security-related functionality, including file system access, is
    provided through the `restricted` subpackage.  This makes it easier to see
    whether commits modify any code with security implications.

2.  Within the `restricted` subpackage, there is a `RestrictedPath` class that
    is a subclass of `pathlib.Path`.  All file path objects that are created
    in response to user data from LaTeX are instances of `RestrictedPath`.
    File system operations are initiated using instances of `RestrictedPath`,
    including creating directories and reading and writing files.

    Before an instance of `RestrictedPath` can access the file system, it is
    resolved
    ([`.resolve()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve))
    to create an absolute path with no symlinks.  Then this resolved path is
    checked against the current working directory, `TEXMFOUTPUT`,
    and `TEXMF_OUTPUT_DIRECTORY` to ensure that the location and type of
    file system operation is allowed.  If not, an error is raised.

    Writing/deleting files is further restricted beyond file location to files
    with names matching this regular expression:
    ```
    [0-9a-zA-Z_-]+\.(?:config|data|errlog|highlight|index|message|style)\.minted
    ```
    All temp files and cache files created by the `minted` LaTeX package and
    the `latex_python` executable match this regular expression.

3.  Some modules and packages such as `json`, `tomllib`, and `latex2pydata`
    provide functions for loading data from files and also functions for
    loading it from strings or bytes.  These modules and packages are not used
    directly.  Instead, the string/bytes loading functions (and only these)
    are imported within the `restricted` subpackage, and then the rest of the
    codebase imports these functions from `restricted`.  For example, to load
    JSON data from file, first a `RestrictedPath` instance is used to read the
    binary data, and then the `json_loads()` function is imported from
    `restricted` to deserialize the data.  While this is not strictly
    necessary, it helps to confine library imports with potential security
    implications to the `restricted` subpackage.  For example, if `json` is
    never imported directly outside of `restricted`, then there is less of a
    danger of thoughtlessly trying to use `json.load()` and then carelessly
    using `open()` instead of `RestrictedPath`.


## `latexminted` and subprocesses

It can be necessary in some cases to run external commands.  Currently, this
is limited to using `kpsewhich` and `initexmf` to access LaTeX configuration,
and using `kpsewhich` to locate files.  The following steps are taken to
ensure safe subprocess access.

1.  The executable must be in a list of approved executables.

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
