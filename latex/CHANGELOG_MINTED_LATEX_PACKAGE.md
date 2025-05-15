# Changelog — minted LaTeX package


## v3.7.0 (2025/05/14)

*  Added support for the Pygments `tokenmerge` filter and enabled it by
   default (#446).  This was the default in `minted` v2 but was lost in the
   transition to v3.

*  Updated minimum required `fvextra` to 2025/05/14 and added support for new
   `fvextra` option `texcomments`.

*  Updated minimum required `latexminted` to v0.6.0.

*  Updated documentation to cover loading `.latexminted_config` config files
   from `$XDG_CONFIG_HOME` (#449).

*  Added FAQ documentation on console/REPL lexers (#267, #388).



## v3.6.0 (2025/03/06)

*  Updated minimum required `latexminted` to v0.5.0.

*  In the `latexminted.py` launcher script, replaced `__version__` with
   `__launcher_version__` and switched to date-based versioning to prevent
   confusion between the launcher script version and the `latexminted` library
   version.



## v3.5.1 (2025/02/12)

*  Fixed a bug from v3.5.0 related to calculating input line numbers that
   caused errors with `\inputminted` (#435).



## v3.5.0 (2025/02/09)

*  Tab characters in inputted temp files with recognized file extensions are
   no longer lost when `highlightmode` is `fastfirst` during the first
   compile, or when `highlightmode` is `fast` (#431).

*  For environments such as `minted`, any error messages generated within
   Python and passed to LaTeX now refer to the starting line of the
   environment, instead of the ending line.  This improves debugging for long
   environments.

*  Updated minimum required `latexminted` to v0.4.0 (#425).



## v3.4.0 (2024/11/17)

*  Replaced temp counter with a macro to prevent issues with commands
   and environments such as `\text` from `amsmath` that modify counter
   behavior (#423).

*  When `highlightmode` causes all code to be highlighted at once, duplicate
   highlighting is now detected and skipped.



## v3.3.0 (2024/11/10)

*  Fixed a bug from v3.2.0 that caused errors with unrestricted shell escape
   (#420).

*  Improved error messages mention the possibility of MiKTeX being used with
   `-aux-directory` or `-output-directory` without setting a
   `TEXMF_OUTPUT_DIRECTORY` environment variable (#419).

*  Updated documentation on shell escape for TeX Live.  The `latexminted`
   executable has been added to TeX Live's list of trusted executables, so
   `-shell-escape` is no longer required.

*  Added support for `fancyvrb` options `reflabel` and `vspace` (#421).



## v3.2.0 (2024/10/29)

*  Fixed compatibility with `\includeonly` by replacing buffer length counters
   with macros (#414).  As part of this, the minimum supported `latex2pydata`
   LaTeX package is now 0.3.0 and the minimum supported `fvextra` is now
   1.9.0.

*  Added new options that allow keywords to be added to a lexer (#416):
   `extrakeywords`, `extrakeywordsconstant`, `extrakeywordsdeclaration`,
   `extrakeywordsnamespace`, `extrakeywordspseudo`, `extrakeywordsreserved`,
   `extrakeywordstype`.  This covers all keyword tokens supported by Pygments
   (https://pygments.org/docs/tokens/#keyword-tokens).

*  Many performance improvements.  When combined with `latexrestricted`
   v0.6.0, these can give a cumulative speedup of over 40% in the case when no
   code needs to be highlighted.

   - Temp files and the cache are now only cleaned up when necessary at the
     end of the document.  Previously, this occurred at the end of each
     compile, unnecessarily increasing compile time.

   - In `latexminted.py`, switched from `platform.system()` to `sys.platform`
     for better performance in detecting operating system.

     Performance reference:  https://github.com/python/cpython/issues/95531.

   - In `latexminted.py` with TeX Live, the value of `TEXMFOUTPUT` is no
     longer retrieved with `kpsewhich` unless it is actually used.  Also fixed
     a bug in parsing `TEXMFOUTPUT` value (whitespace is now stripped).

*  The `debug` package option now records shell escape commands in the log.

*  In config detection, error messages now mention `.errlog.minted` file when
   it exists.



## v3.1.2 (2024/10/07)

*  There is now only a single `\read` allocation for reading temporary files
   when `highlightmode` is set to `fast` or `fastfirst`.  Previously, there
   was one allocation per temp file, which could cause allocation errors when
   several temp files were highlighted during the same compile (#413).



## v3.1.1 (2024/10/03)

*  Fixed bugs in processing temporary files regardless of `highlightmode` from
   v3.1.0.  With `highlightmode=fastfirst` (default), this would cause an
   error during the first compile, but then all subsequent compiles would
   complete correctly.



## v3.1.0 (2024/10/03)

*  All timestamp comparisons that are part of communicating with the
   `latexminted` Python executable now use timestamps that have been processed
   with `\detokenize` (#405).

*  Option processing now wraps values in curly braces to prevent escaping
   issues when options are passed on to other packages for further processing
   (#407).

*  Fixed compatibility with `dvilualatex` (#406).

*  Temporary files with common file extensions are now automatically detected
   and processed correctly regardless of `highlightmode` (#401).  Previously,
   `highlightmode=immediate` was needed for working with temp files that are
   overwritten or deleted during compilation; the default
   `highlightmode=fastfirst` gave an error message during the first compile
   but worked correctly during subsequent compiles.

*  Fixed bug when `cache=false`.  When caching is disabled, `highlightmode` is
   now set to `immediate`.

*  The minimum supported `latexminted` version is now 0.2.0.  The new
   `latexminted` subcommand `cleantemp` is now used instead of `clean` when
   the cache does not require cleaning.  This prevents errors when
   `cache=false`.

*  Fixed docs for `breakbeforeinrun` and `breakafterinrun` (#408).  These had
   not been properly updated after `fvextra` renamed the options.



## v3.0.0 (2024/09/22)

*  Backward compatibility:  The new `minted2` package provides the features of
   `minted` v2.9, the final release before v3.  No additional v2 releases are
   planned; no changes to the `minted2` package are expected.

*  `minted` v3 is a complete rewrite from v2.9.  `minted` v3 includes
   significant changes from `minted` v2 on the LaTeX side, and also uses a new
   `minted`-specific Python executable called `latexminted` to perform syntax
   highlighting.  This executable is specifically designed to meet the
   security requirements for restricted shell escape programs.  Once it has
   passed a security review and is accepted by TeX distributions, it will be
   possible to highlight code without `-shell-escape` and its attendant
   security vulnerabilities.

   Syntax highlighting is still performed with Pygments, but the `pygmentize`
   executable included with Pygments is no longer used.

*  Installing the `minted` package now also installs the `latexminted` Python
   executable and all required Python libraries, including Pygments, within
   your TeX distribution.  These require Python >= 3.8.  If the default Python
   version on `PATH` is < 3.8, then the `latexminted` Python executable will
   attempt to locate a more recent version and run itself with that version in
   a subprocess.

   Manually installing Python libraries is only necessary if you want to use
   plugin packages for Pygments.  In that case, install the `latexminted`
   Python package in a Python installation.  This automatically installs
   `latex2pydata`, `latexrestricted`, and Pygments as dependencies.
   `latexminted` is available from the
   [Python Package Index (PyPI)](https://pypi.org/project/latexminted/).  Then
   install plugin packages for Pygments within the same Python installation.

*  The new `latexminted` Python executable is designed to be compatible with
   the security requirements for restricted shell escape, so that in the
   future TeX distributions can enable `latexminted` without requiring
   `-shell-escape`.  It is possible to benefit from these enhanced security
   capabilities immediately and avoid the need for `-shell-escape`.

   - TeX Live:  Copy the variable `shell_escape_commands` from the
     distribution `texmf.cnf` (typically something like
     `<tex_distro>/texmf-dist/web2c/texmf.cnf`) into the user `texmf.cnf`
     (typically something like `<tex_distro>/texmf.cnf`), and then add
     `latexminted` to the end of the `shell_escape_commands` list.  The
     location of the `texmf.cnf` files can be determined by running
     `kpsewhich -all texmf.cnf`.

   - MiKTeX:  Add a line `AllowedShellCommands[] = latexminted` to the
     existing list of allowed commands in `miktex.ini`.  You may want to
     modify the user-scoped configuration instead of the system-wide
     configuration.  See the
     [MiKTeX documentation](https://docs.miktex.org/manual/miktex.ini.html)
     for more details, particularly `initexmf --edit-config-file <file>`.

*  Errors and warnings that occur within Python are now reported as `minted`
   package errors and warnings within LaTeX in nearly all cases.  It should no
   longer be necessary to look through the compile log for Python errors and
   warnings.  A temp file `*.errlog.minted` containing Python traceback
   information is created in some cases when errors cannot be fully reported
   within LaTeX or more details may be needed.

*  [`latex2pydata`](https://github.com/gpoore/latex2pydata) is now required
   for passing data from LaTeX to Python and then processing it within Python.
   This consists of a LaTeX package, available from
   [CTAN](https://ctan.org/pkg/latex2pydata), and a Python package, available
   from [PyPI](https://pypi.org/project/latex2pydata/).  The LaTeX package can
   typically be installed with your TeX distribution's package manager.  The
   Python package is automatically installed within your TeX distribution when
   `minted` is installed.

*  On the LaTeX side, all syntax highlighting settings are now serialized in
   Python literal format using `latex2pydata` and then saved to a temp file,
   which is loaded on the Python side.  Settings are no longer passed to the
   Python side using command-line arguments.  Temp files for passing data to
   Python are now named using MD5 hashes, instead of using a sanitized version
   of document `\jobname`.  This eliminates an entire class of security issues
   and bugs related to escaping and quoting command-line arguments (#180,
   #276, #298, #322, #338, #354).  It also eliminates bugs related to
   processing settings as a sequence of command-line options, since
   `pygmentize` accumulates some options that are used multiple times rather
   than overwriting earlier values with later values (#258, #337).

*  Options are now handled with `pgfkeys` and `pgfopts`, instead of
   `keyval` and `kvoptions`.

*  Temporary files are no longer created unless the cache needs to be updated
   (or caching is disabled).  All MD5 hashing of code now takes place in
   memory instead of using one temp file per command/environment.

   All temporary files are cleaned up automatically when compiling completes
   without interruption.  All temporary files now have names of the form
   `_<hash>.<role>.minted`.  `<hash>` is an MD5 hash of `\jobname` (if
   `\jobname` is wrapped in double or single quotation marks, these are
   stripped before the MD5 is computed).  `<role>` is the role of the temp
   file: `data` (data passed to Python), `config` (detected system
   configuration), `style` (highlighting style definition), `highlight`
   (highlighted code), or `message` (message passed back to LaTeX by Python
   executable).  `<role>` can also be `errlog` when the Python executable
   encounters an unexpected error that it is not designed to report to the
   LaTeX side; this is not automatically cleaned up.  There are no more
   `<jobname>.pyg` and `<jobname>.out.pyg` files.

*  Several package options are no longer supported and result in errors or
   warnings.

   - `finalizecache`:  No longer needed.  The `frozencache` package option now
      uses the regular cache, rather than requiring a new, special cache
      containing files with sequentially numbered names (#342).  When using
      `frozencache` with `-output-directory`, the `cachedir` package option
      should be used to specify a full relative path to the cache (for
      example, `cachedir=./<output_directory>/_minted`).

   - `outputdir`:  No longer needed (#268).  TeX Live 2024+ saves a custom
     output directory from `-output-directory` in the environment variable
     [`TEXMF_OUTPUT_DIRECTORY`](https://tug.org/texinfohtml/web2c.html#Output-file-location).
     The environment variable `TEXMF_OUTPUT_DIRECTORY` can be set manually in
     other cases.

   - `kpsewhich`:  No longer needed.  `kpsewhich` is now automatically
     invoked as necessary by the `latexminted` Python executable in locating
     files.

   - `draft` and `final`:  These no longer have any effect and result in a
     warning.  They will soon be removed altogether.  Improvements in caching
     have largely eliminated the overhead that `draft` mode was designed to
     avoid, while new features that are implemented purely within Python have
     made it impossible in some cases to typeset code using only LaTeX.  The
     new package options `placeholder` and `verbatim` offer alternatives when
     maximum compilation speed is needed or the `latexminted` Python
     executable is unavailable.

*  New package options:

   - `debug`:  Keep temp files from highlighting to aid in debugging.  Also
     write current file name and line number to log before `\input` of
     highlighted code (#348).

   - `highlightmode`:  Determines when code is highlighted.  The default is
     `fastfirst`.  If a cache for the document exists, then code is
     highlighted immediately.  If a cache for the document does not exist,
     then typeset a placeholder instead of code and highlight all code at the
     end of the document.  This will require a second compile before code is
     typeset, but because all code is highlighted at once, there is less
     overhead and the total time required can be significantly less for
     documents that include many code snippets.  The alternatives are `fast`
     (always highlight at end of document, requiring a second compile) and
     `immediate` (always highlight immediately, so no second compile is
     needed).  `immediate` should be used when typesetting code in external
     temp files that are overwritten during compilation.

     When code is highlighted at the end of the document with `fast` or
     `fastfirst`, any error and warning messages will refer to a location at
     the end of the document rather than the original code location, since
     highlighting occurred at the end of the document.  In this case, messages
     are supplemented with original LaTeX source file names and line numbers
     to aid in debugging.

   - `placeholder`:  Instead of typesetting code, insert a placeholder.  This
     is enabled automatically when working with PGF/TikZ externalization.

   - `verbatim`:  Instead of highlighting code, attempt to typeset it verbatim
     without using the `latexminted` Python executable.  This is not
     guaranteed to be an accurate representation of the code, since some
     features such as `autogobble` require Python.

*  `bgcolor` now uses the new `bgcolor` option from `fvextra` v1.8, rather
   than `snugshade*` from `framed`.  This resolves incompatibilities between
   `bgcolor` and `xleftmargin`/`xrightmargin` (#214), eliminates unneeded
   whitespace before/after the background (#220), prevents text from
   overflowing the background (#278), and provides uniform background height
   for `\mintinline` (#397).  Because `bgcolor` now introduces no additional
   whitespace or padding, existing documents may require some modification.

   Added new option `bgcolorpadding` for modifying padding in background color
   regions.  Added new option `bgcolorvphantom` for setting height of
   background color in inline contexts.

*  Renamed package options `langlinenos` to `lexerlinenos` and
   `inputlanglinenos` to `inputlexerlinenos`.  The old names are still
   supported.

*  The default cache directory name is now `_minted`.  All files within a
   directory now share the same cache, instead of having separate per-document
   caches.  The new `latexminted` Python executable improves cache management
   so that a shared cache functions correctly.  A cache file that is shared by
   multiple documents will not be deleted if one document ceases to use the
   file.

   Document-specific caching as in `minted` v2 can be restored using the
   package option `cachedir`.  For example, for files whose names do not
   contain spaces, simply use `cachedir=\detokenize{_minted-}\jobname`.  For
   files with names that do contain spaces, use a copy of `\jobname` in which
   the wrapping quotation marks have been removed or replaced with other
   characters and the spaces have been replaced with placeholders such as `_`.

*  Cache file names now take the form `<hash>_highlight.minted` and
   `<style>_style.minted`.  `<hash>` is a single MD5 hash of code and options,
   when serialized in Python literal format.  Cache file names no longer use
   two concatenated MD5 hashes, one of code and one of options.  The cache
   directory will also contain files `_<hash>.index.minted`.  These list all
   cache files used by a given document.  In this case, `<hash>` is the MD5
   hash of the document's `\jobname` (if `\jobname` is wrapped in double or
   single quotation marks, these are stripped before the MD5 is computed).

*  Highlighting style names must now match the regular expression
   `^[0-9A-Za-z_-]+$`.  This is checked on the LaTeX side.

*  `\inputminted` is redefined as robust and is usable in movable arguments.

*  `\newminted` now creates an environment that takes an optional argument
   consisting of options, instead of taking no argument.  It still creates a
   starred `*` environment variant that takes a mandatory argument consisting
   of options, but this is only retained for backward-compatibility purposes.

*  Improved fallback behavior in the event of errors.  If code cannot be
   highlighted, it is automatically typeset with a verbatim approximation if
   possible and otherwise replaced by a placeholder.  If a highlighting style
   definition cannot be generated, it is automatically replaced with the
   default style if available, and otherwise a built-in style with no syntax
   highlighting is used.

*  File encoding changes:

   - The new `latexminted` executable assumes that LaTeX output files are
     UTF-8, and saves highlighted code as UTF-8.  That is, LaTeX should be
     configured so that everything is UTF-8.

   - The `encoding` option now defaults to UTF-8.  It is only used in decoding
     files for `\inputminted` and commands based on it.

   - The `outencoding` option is no longer supported.

*  Added new options for including ranges of code based on literal string
   delimiters or regular expressions.  These work with all commands and
   environments, including `\inputminted`.

   - `rangestartstring`:  Select code starting with this string.

   - `rangestartafterstring`:  Select code starting immediately after this
     string.

   - `rangestopstring`:  Select code ending with this string.

   - `rangestopbeforestring`:  Select code ending immediately before this
     string.

   - `rangeregex`:  Select code that matches this regular expression.

   - `rangeregexmatchnumber` [default=`1`]:  If there are multiple
     non-overlapping matches for `rangeregex`, this determines which is
     used.

   - `rangeregexdotall` [default=`false`]:  `.` matches any character
     including the newline.

   - `rangeregexmultiline` [default=`false`]:  `^` and `$` match at
     internal newlines, not just at the start/end of the string.

   If line numbers are displayed, they are based on the range of code that is
   selected; code that is discarded in selecting the range is not considered
   in calculating line numbers.

   String values and regular expressions can be set using text with backslash
   escapes, in a manner analogous to regular (non-raw) Python strings.  Any
   ASCII symbols and punctuation, including those that have special LaTeX
   meaning, can be backslash escaped.  For example, `rangeregex=\\\\.` is
   processed like the Python string `"\\\\."`, becoming the literal text
   `\\.`, which is then interpreted as the regular expression for a literal
   backslash followed by any character.  Alternatively, string values and
   regular expressions can be set using a single macro that, when fully
   expanded (`\edef`), gives the desired literal text.  For example,
   `\def\pattern{\detokenize{\\.}}` and then `rangeregex=\pattern` would be
   equivalent to `rangeregex=\\\\.`.

*  There is now official support for custom lexers.  Custom lexers that are
   installed as Pygments [plugins](https://pygments.org/docs/plugins/) have
   always been supported, since Pygments can find them automatically.
   However, custom lexers in the form of `*.py` files in the document
   directory have not officially been supported.

   Custom lexers can be specified in place of builtin lexers.  For example,
   `\inputminted{lexer.py}{<file>}` or
   `\inputminted{./path/lexer.py:LexerClass}{<file>}`.

   Custom lexers in the form of `*.py` files are not automatically enabled,
   since they are equivalent to arbitrary code execution and are thus a
   significant security risk.  To enable custom lexers, create a file
   `.latexminted_config`.  This can be in your home directory (as found by
   Python's `pathlib.Path.home()`) or in `TEXMFHOME`; if this file is found in
   both locations, settings from the TeX location overwrite settings from the
   home directory.  It is also possible to enable a `.latexminted_config` file
   in your document directory; see the documentation for
   `.latexminted_config`.  This file must contain data in Python literal,
   JSON, or TOML format.  TOML requires Python >= 3.11.  The data must contain
   an entry equivalent to this Python data:
   ```
   {
      "custom_lexers": {
         "<lexer file name>": "<SHA-256 hash of lexer file>"
      }
   }
   ```
   `<lexer file name>` is just the name of the file, with no path or class
   included.  For example, for `./path/lexer.py:LexerClass` it would be just
   `lexer.py`.  Any number of file names and hashes can be provided.

*  Enhancements of existing options:

   - `codetagify` now supports comma-delimited lists of strings, not just
     space-delimited lists (#126).

*  New options:

   - `envname`:  Name of the environment that wraps typeset code.  By default,
     it is `Verbatim` in block contexts and `VerbEnv` in inline contexts.
     This is compatible with `fancyvrb`'s `BVerbatim` (#281).

     Implementation note:  Code is actually wrapped a `MintedVerbatim`
     environment, and then this is redefined to be equivalent to `envname`
     (see the new option `literalenvname`).

   - `literalenvname`:  This is the name of the environment that literally
     appears in highlighted code output as a wrapper around the code.  By
     default it is `MintedVerbatim`.  This environment is redefined to be
     equivalent to the current value of `envname`.  There should be few if any
     situations where modifying `literalenvname` rather than `envname` is
     actually necessary.

   - `literatecomment`:   This is for compatibility with literate programming
     formats, such as the `.dtx` format commonly used for writing LaTeX
     packages.  If all lines of code begin with `<literatecomment>`, then
     `<literatecomment>` is removed from the beginning of all lines.  For
     example, for `.dtx`, `literatecomment=\%`.

   - `listparameters`:  Previously unsupported `fancyvrb` option (#256).

   - `breakanywhereinlinestretch`:  New `fvextra` option.

*  `gobble` is now applied to code before syntax highlighting and no longer
   uses the Pygments `gobble` filter, which operates on the token stream
   generated by a lexer.  This makes `gobble` and `autogobble` behave in the
   same manner.  The Pygments `gobble` filter is still accessible via the new
   option `gobblefilter` (#379).

*  Standard catcodes are now enforced in reading the optional argument of
   environments that wrap Pygments output.  This prevents issues with
   `babel`'s `magyar` (#382).



## v2.9 (2023/12/18)

*  This is expected to be the last release of `minted` v2.x.  If so, it will
   then become the new package `minted2` for backward compatibility.

*  Added new option `ignorelexererrors`.  When lexer errors are shown in
   highlighted output (default), they are typically displayed as red boxes
   that surround the relevant text.  When lexer errors are ignored, the
   literal text that caused lexer errors is shown but there is no indication
   that it caused errors (#374).

*  There is now a warning if `fvextra` version is less than 1.5.



## v2.8 (2023/09/12)

*   Under non-Windows operating systems, detect executables with `command -v`
    rather than `which` to provide better cross-platform support (#345).

*   Added new package option `inputlanglinenos`.  This extends the existing
    `langlinenos` to cover `\inputminted` as well (#361).

*   Improved and updated Pygments documentation (#339).

*   Improved `\mintinline` documentation to address packages that redefine
    `\section` (#368).

*   Added support for `fvextra` options `breakafterinrun` and
    `breakbeforeinrun` (#358).  In `fvextra` version 1.5, `breakaftergroup`
    and `breakbeforegroup` were renamed to `breakafterinrun` and
    `breakbeforeinrun` to avoid naming ambiguity with new options.  The old
    options `breakaftergroup` and `breakbeforegroup` are no longer supported.

*   Added `DEPENDS.txt` (#331).

*   Removed unnecessary dependency on `calc` package (#313).

*   Added documentation in FAQ about copy and paste limitations (#302).

*   Added note on `text` lexer to documentation (#274).



## v2.7 (2022/12/12)

*   Reimplemented `\mintinline` to use `fvextra`'s argument reading and
    processing macros, and to use `fvextra`'s `\Verb` internally.
    `\mintinline` now works with all line breaking options supported by
    `fvextra`'s `\Verb`, including `breakanywhere` (#329, #340).  It now
    gives better results when used inside other commands, since it uses
    `fvextra`'s retokenization macros.  It is now compatible with `hyperref`
    for PDF strings such as bookmarks.

*   Reimplemented `\newmintinline` based on new `\mintinline`.

*   Reimplemented `\mint` to use `fvextra`'s argument reading and processing
    macros.  It now gives better results when used inside other commands,
    since it uses `fvextra`'s retokenization macros.  Fixed a bug that caused
    a continued paragraph after `\mint` to be indented (#218).

*   Reimplemented `\newmint` based on new `\mint`.  Commands created with
    `\newmint` can now use curly braces as delimiters, just like `\mint`
    (#254).

*   Settings passed to `pygmentize` as command-line options are now quoted.
    This prevents `escapeinside` characters from being interpreted as special
    shell characters (#179, #262).

*   Fixed bug with `autogobble` that produced incorrect dedent when using
    `lastline` with the lines beyond `lastline` having less indentation than
    the selected range (#326).

*   Fixed unintended line breaks after hyphens under LuaTeX (#263).

*   Added warning to documentation of `\inputminted` regarding filenames
    and shell command execution (#338).



## v2.6 (2021/12/24)

*   `autogobble` automatically uses `python` or `python3` executables,
    depending on availability, instead of requiring `python`.  A custom
    executable can be specified by redefining `\MintedPython` (#277, #287).

*   Fixed `autogobble` compatibility with `fancyvrb` 4.0+ (#315, #316).

*   Pygments style names may now contain arbitrary non-whitespace characters.
    Previously, style names containing digits and some punctuation characters
    were incompatible (#210, #294, #299, #317).  Pygments macros are now only
    defined just before use locally within `minted` commands and environments,
    rather than globally.  Pygments macros now always use a `\PYG` prefix
    regardless of style, rather than a prefix of the form `\PYG<style>` (for
    example, what was previously `\PYGdefault` is now simply `\PYG`).

*   Removed Python-based MD5 hashing for XeTeX, which was necessary before
    XeTeX added `\mdfivesum` in 2017.

*   The default for `stripnl` is now `false`, so that original code is
    preserved exactly by default (#198).

*   Added support for `fontencoding` option from `fvextra` (#208).

*   Added note to FAQ about getting `texi2pdf` to work with `minted` given
    `texi2pdf`'s assumptions about temp files (#186).

*   Reimplemented `bgcolor` option to be compatible with `color` package.



## v2.5 (2017/07/19)

*  The default placement for the `listing` float is now `tbp` instead of `h`,
   to parallel `figure` and `table` and also avoid warnings caused by `h`
   (#165).  The documentation now contains information about changing default
   placement.  The `float` package is no longer loaded when the `newfloat`
   package option is used.

*  Added support for `*nchars` options from `fvextra` v1.3 that allow setting
   `breaklines`-related indentation in terms of a number of characters, rather
   than as a fixed dimension.

*  Fixed incompatibility with `babel magyar` (#158).

*  Added support for `beamer` overlays with `beameroverlays` option (#155).

*  Comments in the Pygments LaTeX style files no longer appear as literal
   text when `minted` is used in `.dtx` files (#161).

*  `autogobble` now works with package option `kpsewhich` (#151).  Under
   Windows, the `kpsewhich` option no longer requires PowerShell.

*  Fixed a bug that prevented `finalizecache` from working with `outputdir`
   (#149).

*  Fixed a bug with `firstline` and `lastline` that prevented them from
   working with the `minted` environment (#145).

*  Added note on `breqn` conflicts to FAQ (#163).



## v2.4.1 (2016/10/31)

*  Single quotation marks in `\jobname` are now replaced with underscores in
   `\minted@jobname` to prevent quoting errors (#137).

*  The `autogobble` option now takes `firstline` and `lastline` into account
   (#130).

*  Fixed `numberblanklines`, which had been lost in the transition to v2.0+
   (#135).



## v2.4 (2016/07/20)

*  Line breaking and all associated options are now completely delegated to
   `fvextra`.

*  Fixed a bug from v2.2 that could cause the first command or environment to
   vanish when `cache=false` (related to work on `\MintedPygmentize`).



## v2.3 (2016/07/14)

*  The `fvextra` package is now required.  `fvextra` extends and patches
   `fancyvrb`, and includes improved versions of `fancyvrb` extensions that
   were formerly in `minted`.

*  As part of `fvextra`, the `upquote` package is always loaded.  `fvextra`
   brings the new option `curlyquotes`, which allows curly single quotation
   marks instead of the literal backtick and typewriter single quotation mark
   produced by `upquote`.  This allows the default `upquote` behavior to be
   disabled when desired.

*  Thanks to `fvextra`, the options `breakbefore`, `breakafter`, and
   `breakanywhere` are now compatible with non-ASCII characters under
   pdfTeX (#123).

*  Thanks to `fvextra`, `obeytabs` no longer causes lines in multi-line
   comments or strings to vanish (#88), and is now compatible with
   `breaklines` (#99).  `obeytabs` will now always give correct results with
   tabs used for indentation.  However, tab stops are not guaranteed to be
   correct for tabs in the midst of text.

*  `fvextra` brings the new options `space`, `spacecolor`, `tab`, and
    `tabcolor` that allow these characters and their colors to be redefined
    (#98).  The tab may now be redefined to a flexible-width character such
    as `\rightarrowfill`.  The visible tab will now always be black by default,
    instead of changing colors depending on whether it is part of indentation
    for a multiline string or comment.

*  `fvextra` brings the new options `highlightcolor` and `highlightlines`,
   which allow single lines or ranges of lines to be highlighted based on line
   number (#124).

*  `fvextra` brings the new options `numberfirstline`, `stepnumberfromfirst`,
   and `stepnumberoffsetvalues` that provide better control over line
   numbering when `stepnumber` is not 1.

*  Fixed a bug from v2.2.2 that prevented `upquote` from working.



## v2.2.2 (2016/06/21)

*  Fixed a bug introduced in v2.2 that prevented setting the Pygments style in
   the preamble.  Style definitions are now more compatible with using
   `\MintedPygmentize` to call a custom `pygmentize`.



## v2.2.1 (2016/06/15)

*  The `shellesc` package is loaded before `ifplatform` and other packages
   that might invoke `\write18` (#112).

*  When caching is enabled, XeTeX uses the new `\mdfivesum` macro from TeX
   Live 2016 to hash cache content, rather than using `\ShellEscape` with
   Python to perform hashing.



## v2.2 (2016/06/08)

*  All uses of `\ShellEscape` (`\write18`) no longer wrap file names and paths
   with double quotes.  This allows a cache directory to be specified relative
   to a user's home directory, for example, `~/minted_cache`.  `cachedir` and
   `outputdir` paths containing spaces will now require explicit quoting of
   the parts of the paths that contain spaces, since `minted` no longer
   supplies quoting.  See the updated documentation for examples (#89).

*  Added `breakbefore`, `breakbeforegroup`, `breakbeforesymbolpre`, and
   `breakbeforesymbolpost`.  These parallel `breakafter*`.  It is possible to
   use `breakbefore` and `breakafter` for the same character, so long as
   `breakbeforegroup` and `breakaftergroup` have the same setting (#117).

*  Added package options `finalizecache` and `frozencache`.  These allow the
   cache to be prepared for (`finalizecache`) and then used (`frozencache`) in
   an environment in which `-shell-escape`, Python, and/or Pygments are not
   available.  Note that this only works if `minted` content does not need to
   be modified, and if no settings that depend on Pygments or Python need to
   be changed (#113).

*  Style names containing hyphens and underscores (`paraiso-light`,
   `paraiso-dark`, `algol_nu`) now work (#111).

*  The `shellesc` package is now loaded, when available, for compatibility
   with LuaTeX 0.87+ (TeX Live 2016+, etc.).  `\ShellEscape` is now used
   everywhere instead of `\immediate\write18`.  If `shellesc` is not available,
   then a `\ShellEscape` macro is created.  When `shellesc` is loaded, there
   is a check for versions before v0.01c to patch a bug in v0.01b (present in
   TeX Live 2015) (#112).

*  The `bgcolor` option now uses the `snugshade*` environment from the `framed`
   package, so `bgcolor` is now compatible with page breaks.  When `bgcolor`
   is in use, immediately preceding text will no longer push the `minted`
   environment into the margin, and there is now adequate spacing from
   surrounding text (#121).

*  Added missing support for `fancyvrb`'s `labelposition` (#102).

*  Improved fix for TikZ externalization, thanks to Patrick Vogt (#73).

*  Fixed `breakautoindent`; it was disabled in version 2.1 due to a bug in
   `breakanywhere`.

*  Properly fixed handling of `\MintedPygmentize` (#62).

*  Added note on incompatibility of `breaklines` and `obeytabs` options.
   Trying to use these together will now result in a package error (#99).
   Added note on issues with `obeytabs` and multiline comments (#88).  Due to
   the various `obeytabs` issues, the docs now discourage using `obeytabs`.

*  Added note to FAQ on `fancybox` and `fancyvrb` conflict (#87).

*  Added note to docs on the need for `\VerbatimEnvironment` in environment
   definitions based on `minted` environments.



## v2.1 (2015/09/09)

*  Changing the highlighting style now no longer involves re-highlighing
   code.  Style may be changed with almost no overhead.

*  Improved control of automatic line breaks.  New option `breakanywhere`
   allows line breaks anywhere when `breaklines=true`.  The pre-break and
   post-break symbols for these types of breaks may be set with
   `breakanywheresymbolpre` and `breakanywheresymbolpost` (#79).  New option
   `breakafter` allows specifying characters after which line breaks are
   allowed.  Breaks between adjacent, identical characters may be controlled
   with `breakaftergroup`.  The pre-break and post-break symbols for these
   types of breaks may be set with `breakaftersymbolpre` and
   `breakaftersymbolpost`.

*  `breakbytoken` now only breaks lines between tokens that are separated by
   spaces, matching the documentation.  The new option `breakbytokenanywhere`
   allows for breaking between tokens that are immediately adjacent.  Fixed a
   bug in `\mintinline` that produced a following linebreak when
   `\mintinline` was the first thing in a paragraph and `breakbytoken` was
   true (#77).

*  Fixed a bug in draft mode option handling for `\inputminted` (#75).

*  Fixed a bug with `\MintedPygmentize` when a custom `pygmentize` was
   specified and there was no `pygmentize` on the default path (#62).

*  Added note to docs on caching large numbers of code blocks under OS X (#78).

*  Added discussion of current limitations of `texcomments` (#66) and
   `escapeinside` (#70).

*  PGF/Ti*k*Z externalization is automatically detected and supported
   (#73).

*  The package is now compatible with LaTeX files whose names contain spaces (#85).



## v2.0 (2015/01/31)

*  Added the compatibility package `minted1`, which provides the `minted` 1.7
   code.  This may be loaded when 1.7 compatibility is required.  This package
   works with other packages that `\RequirePackage{minted}`, so long as it is
   loaded first.

*  Moved all old `\changes` into `changelog`.



## Development releases for 2.0 (2014-January 2015)

*  Caching is now on by default.

*  Fixed a bug that prevented compiling under Windows when file names
   contained commas.

*  Added `breaksymbolleft`, `breaksymbolsepleft`,
   `breaksymbolindentleft`, `breaksymbolright`, `breaksymbolsepright`,
   and `breaksymbolindentright` options. `breaksymbol`,
   `breaksymbolsep`, and `breaksymbolindent` are now aliases for the
   correspondent `*left` options.

*  Added `kpsewhich` package option. This uses `kpsewhich` to locate
   the files that are to be highlighted. This provides compatibility
   with build tools like `texi2pdf` that function by modifying
   `TEXINPUTS` (#25).

*  Fixed a bug that prevented `\inputminted` from working with `outputdir`.

*  Added informative error messages when Pygments output is missing.

*  Added `final` package option (opposite of `draft`).

*  Renamed the default cache directory to `_minted-<jobname>` (replaced
   leading period with underscore). The leading period caused the cache
   directory to be hidden on many systems, which was a potential source
   of confusion.

*  `breaklines` and `breakbytoken` now work with `\mintinline` (#31).

*  `bgcolor` may now be set through `\setminted` and `\setmintedinline`.

*  When math is enabled via `texcomments`, `mathescape`, or
   `escapeinside`, space characters now behave as in normal math by
   vanishing, instead of appearing as literal spaces. Math need no
   longer be specially formatted to avoid undesired spaces.

*  In default value of `\listoflistingscaption`, capitalized “Listings” so that
   capitalization is consistent with default values for other lists
   (figures, tables, algorithms, etc.).

*  Added `newfloat` package option that creates the `listing`
   environment using `newfloat` rather than `float`, thus providing
   better compatibility with the `caption` package (#12).

*  Added support for Pygments option `stripall`.

*  Added `breakbytoken` option that prevents `breaklines` from breaking
   lines within Pygments tokens.

*  `\mintinline` uses a `\colorbox` when `bgcolor` is set, to give more
   reasonable behavior (#57).

*  For PHP, `\mintinline` automatically begins with `startinline=true` (#23).

*  Fixed a bug that threw off line numbering in `minted` when
   `langlinenos=false` and `firstnumber=last`. Fixed a bug in `\mintinline` that
   threw off subsequent line numbering when `langlinenos=false` and
   `firstnumber=last`.

*  Improved behavior of `\mint` and `\mintinline` in `draft` mode.

*  The `\mint` command now has the additional capability to take code
   delimited by paired curly braces `{}`.

*  It is now possible to set options only for `\mintinline` using the new
   `\setmintedinline` command. Inline options override options specified via
   `\setminted`.

*  Completely rewrote option handling. `fancyvrb` options are now handled on the
   LaTeX side directly, rather than being passed to Pygments and then
   returned. This makes caching more efficient, since code is no longer
   rehighlighted just because options changed.

*  Fixed buffer size error caused by using `cache` with a very large
   number of files (#61).

*  Fixed `autogobble` bug that caused failure under some operating
   systems.

*  Added support for `escapeinside` (requires Pygments 2.0+; #38).

*  Fixed issues with XeTeX and caching (#40).

*  The `upquote` package now works correctly with single quotes when
   using Pygments 1.6+ (#34).

*  Fixed caching incompatibility with Linux and OS X under xelatex
   (#18 and #42).

*  Fixed `autogobble` incompatibility with Linux and OS X.

*  `\mintinline` and derived commands are now robust, via `\newrobustcmd`
   from `etoolbox`.

*  Unused styles are now cleaned up when caching.

*  Fixed a bug that could interfere with caching (#24).

*  Added `draft` package option (#39). This typesets all code using
   `fancyvrb`; Pygments is not used. This trades syntax highlighting
   for maximum speed in compiling.

*  Added automatic line breaking with `breaklines` and related options
   (#1).

*  Fixed a bug with boolean options that needed a False argument to
   cooperate with `\setminted` (#48).



## v2.0-alpha3 (2013/12/21)

*  Added `autogobble` option.  This sends code through Python's
   `textwrap.dedent()` to remove common leading whitespace.

*  Added package option `cachedir`.  This allows the directory in which
   cached content is saved to be specified.

*  Added package option `outputdir`.  This allows an output directory for
   temporary files to be specified, so that the package can work with
   LaTeX's `-output-directory` command-line option.

*  The `kvoptions` package is now required.  It is needed to process
   key-value package options, such as the new `cachedir` option.

*  Many small improvements, including better handling of paths under
   Windows and improved key system.



## v2.0-alpha2 (2013/08/21)

*  `\DeleteFile` now only deletes files if they do indeed exist.  This
   eliminates warning messages due to missing files.

*  Fixed a bug in the definition of `\DeleteFile` for non-Windows systems.

*  Added support for Pygments option `stripnl`.

*  Settings macros that were previously defined globally are now defined
   locally, so that `\setminted` may be confined by `\begingroup...\endgroup`
   as expected.

*  Macro definitions for a given style are now loaded only once per document,
   rather than once per command/environment.  This works even without caching.

*  A custom script/executable may now be substituted for `pygmentize` by
   redefining `\MintedPygmentize`.



## v2.0alpha (2013/07/30)

*  Added the package option `cache`. This significantly increases
   compilation speed by caching old output. For example, compiling the
   documentation is around 5x faster.

*  New inline command `\mintinline`. Custom versions can be created via
   `\newmintinline`. The command works inside other commands (for example,
   footnotes) in most situations, so long as the percent and hash
   characters are avoided.

*  The new `\setminted` command allows options to be specified at the
   document and language levels.

*  All extended characters (Unicode, etc.) supported by `inputenc` now
   work under the pdfTeX engine. This involved using `\detokenize` on
   everything prior to saving.

*  New package option `langlinenos` allows line numbering to pick up
   where it left off for a given language when `firstnumber=last`.

*  New options, including `style`, `encoding`, `outencoding`,
   `codetagify`, `keywordcase`, `texcomments` (same as `texcl`),
   `python3` (for the `PythonConsoleLexer`), and `numbers`.

*  `\usemintedstyle` now takes an optional argument to specify the style for a
   particular language, and works anywhere in the document.

*  `xcolor` is only loaded if `color` isn’t, preventing potential
   package clashes.



## v1.7 (2011/09/17)

*  Options for float placement added [2011/09/12]

*  Fixed `tabsize` option [2011/08/30]

*  More robust detection of the `-shell-escape` option [2011/01/21]

*  Added the `label` option [2011/01/04]

*  Installation instructions added [2010/03/16]

*  Minimal working example added [2010/03/16]

*  Added PHP-specific options [2010/03/14]

*  Removed unportable flag from Unix shell command [2010/02/16]


## v1.6 (2010/01/31)

*  Added font-related options [2010/01/27]

*  Windows support added [2010/01/27]

*  Added command shortcuts [2010/01/22]

*  Simpler versioning scheme [2010/01/22]



## v0.1.5 (2010/01/13)

*  Added `fillcolor` option [2010/01/10]

*  Added float support [2010/01/10]

*  Fixed `firstnumber` option [2010/01/10]

* Removed `caption` option [2010/01/10]



## v0.0.4 (2010/01/08)

*  Initial version [2010/01/08]
