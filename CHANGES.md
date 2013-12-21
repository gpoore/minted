v2.0-alpha3 (2013/12/21)

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


v2.0-alpha2 (2013/08/21)

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


v2.0alpha (2013/07/30):

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