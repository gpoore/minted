# Changelog: `latexminted` — Python library for LaTeX minted package

## v0.2.0 (dev)

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
