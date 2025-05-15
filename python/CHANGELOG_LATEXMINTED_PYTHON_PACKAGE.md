# Changelog: `latexminted` — Python library for LaTeX minted package



## v0.6.0 (2025-05-14)

*  Added support for the Pygments `tokenmerge` filter (#446).

*  `.latexminted_config` config files are now loaded from
   `$XDG_CONFIG_HOME/latexminted` (#449), followed by the user home directory,
   `TEXMFHOME`, and (if enabled) the current working directory.  Config files
   later in the sequence override settings from config files that were loaded
   earlier.  If `$XDG_CONFIG_HOME` is not set, it defaults to `~/.config`.



## v0.5.1 (2025-03-27)

*  Fixed a bug from v0.5.0 in determining whether `.latexminted_config` is
   readable (#443).



## v0.5.0 (2025-03-06)

*  Improved handling of `.latexminted_config`.  Invalid config data no longer
   causes an uncaught error, resulting in incorrect error messages on the
   LaTeX side (#438).  An empty config file no longer causes an uncaught error
   under some circumstances.

*  Improved `--help` message (#404).

*  Added man page for Python executable (#403).

*  Updated dependency requirements to `latex2pydata` >= 0.5.0 and
   `latexrestricted` >= 0.6.2.

*  When loading data, switched from `schema_missing='rawstr'` to
   `schema_missing='verbatim'` for full compatibility with `latex2pydata`
   v0.5.0.



## v0.4.0 (2025-02-09)

*  `rangeregex` is now compatible with Python < 3.11.

*  Errors in compiling regular expressions for `rangeregex` are now always
   caught and translated into LaTeX errors.

*  Improved error messages when `rangeregex`, possibly combined with
   `rangeregexmatchnumber`, fails to find a match.

*  A security error related to `.latexminted_config` is no longer always
   raised when dotfiles are writable by LaTeX (`openout_any=a`).  An error is
   now raised only when `.latexminted_config` actually exists under these
   circumstances.



## v0.3.2 (2024-11-24)

*  `pyproject.toml`:  explicitly set `build-backend` (#424).



## v0.3.1 (2024-11-12)

*  Fixed a bug in config detection that caused an error when a data file from
   LaTeX cannot be located.



## v0.3.0 (2024-10-29)

*  Added support for new keywords options (#416):  `extrakeywords`,
   `extrakeywordsconstant`, `extrakeywordsdeclaration`,
   `extrakeywordsnamespace`, `extrakeywordspseudo`, `extrakeywordsreserved`,
   `extrakeywordstype`.

*  Refactored version handling in `cmdline.py` to avoid unnecessary imports.

*  Improved `.errlog.minted` files.  Improved layout and added traceback
   information for the origin in the LaTeX document.  Fixed a bug that could
   cause `.errlog.minted` files to be deleted when they should be kept.
   `.errlog.minted` files now contain all error data from a compile,
   regardless of `highlightmode` setting.  Previously, only the data from the
   last error was kept under some circumstances when `highlightmode` was not
   `immediate`.



## v0.2.0 (2024-10-03)

*  All config data passed back to LaTeX is now processed with `\detokenize`
   (#405).

*  In a cache, `*.index.minted` files are now overwritten only when the data
   they contain is modified.  This fixes compatibility with build tools
   (T-F-S/tcolorbox/issues/294).

*  Fixed a bug that could prevent a cache from being fully cleaned when it is
   shared by multiple documents.

*  All file reading and writing for files received from/sent to LaTeX is now
   UTF-8 (#411).

*  The cache path is now processed correctly when it is an empty string,
   instead of resulting in an error, so the `minted` package will now function
   when `cache=false`.

*  Refactored the `cleanfile` subcommand into `cleanconfig`.  This is more
   descriptive for actual usage and allows all subcommands to take the same
   arguments.

*  Added subcommand `cleantemp`, which only cleans temp files, not cache
   files.

*  All subcommands now take exactly the same arguments.

*  Added short summary and links to `latexminted --version` (#404).



## v0.1.0 (2024-09-22)

*  Initial release.
