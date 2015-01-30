# Changes

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
