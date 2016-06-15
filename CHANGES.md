# Changes


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
