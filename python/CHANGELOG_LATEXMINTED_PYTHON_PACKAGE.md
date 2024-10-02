# Changelog: `latexminted` — Python library for LaTeX minted package

## v0.2.0 (dev)

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



## v0.1.0 (2024-09-22)

*  Initial release.
