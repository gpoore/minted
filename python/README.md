# `latexminted` — Python library for LaTeX minted package

This Python package provides the Python side of the LaTeX
[`minted`](https://github.com/gpoore/minted) package.  It performs syntax
highlighting using the [Pygments](https://pygments.org/) library.  It also
provides several code formatting and manipulation features implemented in
Python that would be difficult to perform in LaTeX, such as dedenting code and
extracting code snippets from source files using regular expressions.

This package should only be installed manually if you need to use plugin
packages for Pygments.  The package is bundled within TeX distributions as a
Python wheel along with the LaTeX `minted` package.  Installing the LaTeX
`minted` package with your TeX distribution's package manager will also
install the `latexminted` Python package and all required Python libraries
within the TeX installation.  If you do need Pygments plugins, then install
`latexminted` manually along with Pygments in a Python installation.  Make
sure that the `latexminted` executable that is created as part of this process
has precedence on `PATH` over the `latexminted` executable in your TeX
installation.  For Windows, precedence on either the system `PATH` or the user
`PATH` is usually sufficient, as long as the TeX installation is in a typical
location and any user Python executable is within a Python installation under
the user's home directory.

This Python package is specifically designed to be compatible with the LaTeX
security requirements for restricted shell escape executables.  These trusted
executables can run during LaTeX compilation without requiring `-shell-escape`
or similar command-line options that allow arbitrary shell commands to be
executed.


## Configuration

Several `minted` settings with security implications can be customized with a
config file `.latexminted_config`.  This config file is loaded by the
`latexminted` Python executable when it runs.

The `latexminted` Python executable looks for `.latexminted_config` files in
the following locations:

  * User home directory, as found by Python's
    [pathlib.Path.home()](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home).

  * `TEXMFHOME`.  With MiKTeX on systems with multiple MiKTeX installations,
    this will be the `TEXMFHOME` from the first MiKTeX installation on `PATH`.
    With TeX Live on Windows systems with multiple TeX Live installations,
    this will be the `TEXMFHOME` from the first TeX Live installation on
    `PATH`.  In all other cases, `TEXMFHOME` will correspond to the currently
    active TeX installation.  See the
    [`latexrestricted`](https://github.com/gpoore/latexrestricted)
    documentation for details.  `latexrestricted` is used by the `latexminted`
    Python executable to retrieve the value of `TEXMFHOME`.

  * The current TeX working directory.  Note that `enable_cwd_config` must be
    set `true` in the `.latexminted_config` in the user home directory or in
    the `TEXMFHOME` directory to enable this; `.latexminted_config` in the
    current TeX working directory is not enabled by default for security
    reasons.  Even when a config file in the current TeX working directory is
    enabled, it cannot be used to modify certain security-related settings.

Overall configuration is derived by merging all config files, with later files
in the list above having precedence over earlier files.  Boolean and string
values are overwritten by later config files.   Collection values (currently
only sets derived from lists) are merged with earlier values.

### File format

The `.latexminted_config` file may be in Python literal format (dicts and
lists of strings and bools), JSON, or TOML (requires Python 3.11+).  It must
be encoded as UTF-8.

### Settings

* `security: dict[str, str | bool]`:  These settings relate to `latexminted`
  security.  They can only be set in `.latexminted_config` in the user home
  directory or in `TEXMFHOME`.  They cannot be set in `.latexminted_config` in
  the current TeX working directory.

  - `enable_cwd_config: bool = False`:  Load a `.latexminted_config` file from
    the current TeX working directory if it exists.  This is disabled by
    default because the config file can enable `custom_lexers`, which is
    equivalent to arbitrary code execution.

  - `file_path_analysis: "resolve" | "string" = "resolve"`:  This specifies
    how `latexminted` determines whether files are readable and writable.
    Relative file paths are always treated as being relative to the current
    TeX working directory.

    With `resolve`, any symlinks in file paths are resolved with the file
    system before paths are compared with permitted LaTeX read/write
    locations.  Arbitrary relative paths including `..` are allowed so long as
    the final location is permitted.

    With `string`, paths are analyzed as strings in comparing them with
    permitted LaTeX read/write locations.  This follows the approach taken in
    TeX's file system security.  Paths cannot contain `..` to access a parent
    directory, even if the parent directory is a valid location.  Because
    symlinks are not resolved with the file system, it is possible to access
    locations outside permitted LaTeX read/write locations, if the permitted
    locations contain symlinks to elsewhere.

  - `permitted_pathext_file_extensions: list[str]`:  As a security measure
    under Windows, LaTeX cannot write files with file extensions in `PATHEXT`,
    such as `.bat` and `.exe`.  This setting allows `latexminted` to write
    files with the specified file extensions, overriding LaTeX security.  File
    extensions should be in the form `.<ext>`, for example, `.bat`.  This
    setting is used in extracting source code from LaTeX documents and saving
    it in standalone source files.

    When these file extensions are enabled for writing, as a security measure
    `latexminted` will only allow them to be created in *subdirectories* of
    the current TeX working directory, `TEXMFOUTPUT`, and
    `TEXMF_OUTPUT_DIRECTORY`.  These files cannot be created directly under
    the TeX working directory, `TEXMFOUTPUT`, and `TEXMF_OUTPUT_DIRECTORY`
    because those locations are more likely to be used as a working directory
    in a shell, and thus writing executable files in those locations would
    increase the risk of accidental code execution.

* `custom_lexers: dict[str, str | list[str]]`:  This is a mapping of custom
  lexer file names to SHA256 hashes.  Only custom lexers with these file names
  and the corresponding hashes are permitted.  Lists of hashes are allowed to
  permit multiple versions of a lexer with a given file name.  All other
  custom lexers are prohibited, because loading custom lexers is equivalent to
  arbitrary code execution.  For example:

  ```
  "custom_lexers": {
    "mylexer.py": "<sha256>"
  }
  ```

  Note that this only applies to custom lexers in standalone Python files.
  Lexers that are installed within Python as plugin packages work
  automatically with Pygments and do not need to be enabled separately.
  However, in that case it is necessary to install `latexminted` and Pygments
  within a Python installation.  When TeX package managers install
  `latexminted` and Pygments within a TeX installation, these are not
  compatible with Pygments plugin packages.
