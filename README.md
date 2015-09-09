[![flattr](https://api.flattr.com/button/flattr-badge-large.png)][flattr]

# minted — highlighted source code for LaTeX


## Overview

`minted` is a LaTeX package that facilitates expressive syntax highlighting 
using the Pygments library.  The package also provides options to customize 
the highlighted source code output using `fancyvrb`.

For instance, this code:

``` latex
\begin{minted}[mathescape,
               linenos,
               numbersep=5pt,
               gobble=2,
               frame=lines,
               framesep=2mm]{csharp}
string title = "This is a Unicode π in the sky"
/*
Defined as $\pi=\lim_{n\to\infty}\frac{P_n}{d}$ where $P$ is the perimeter
of an $n$-sided regular polygon circumscribing a
circle of diameter $d$.
*/
const double pi = 3.1415926535
\end{minted}
```

will produce the following rendering:

![screenshot](http://i.stack.imgur.com/OLUjl.png)

See the [documentation](https://github.com/gpoore/minted/blob/master/source/minted.pdf)
for examples and installation instructions.


## Moving from version 1.7

Transitioning from `minted` 1.7 to 2.0+ should require no changes in almost 
all cases.  Version 2 provides the same interface and all of the same 
features.

In cases when custom code was used to hook into the `minted` internals, it 
may still be desirable to use the old `minted` 1.7.  For those cases, the 
new package `minted1` is provided.  Simply load this before any other package 
attempts to load `minted`, and you will have the code from 1.7.

A brief summary of new features in version 2 is provided below.  More detail 
is available in `CHANGES.md`, or the Version History in `minted.pdf`.

*  New inline command `\mintinline`.

*  Support for caching highlighted code with new package option `cache`.
   This drastically reduces package overhead.  Caching is on by default.  A 
   cache directory called `_minted-<document name>` will be created in the 
   document root directory.  This may be modified with the `cachedir` package 
   option.

*  Automatic line breaking for all commands and environments with new option
   `breaklines`.  Many additional options for customizing line breaking,
   including `breakanywhere` (line breaks anywhere, not just at spaces) and 
   `breakafter` (line breaks after specified characters).

*  Support for Unicode under the pdfTeX engine.

*  Set document-wide options using `\setminted{<opts>}`.  Set 
   language-specific options using `\setminted[<lang>}{<opts>}`.  Similarly, 
   set inline-specific options using `\setmintedinline`.

*  Package option `langlinenos`:  do line numbering by language.

*  Many new options, including `encoding`, `autogobble`, and `escapeinside`
   (requires Pygments 2.0+).

*  New package option `outputdir` provides compatibility with command-line 
   options `-output-directory` and `-aux-directory`.

*  New package option `draft` disables Python use to give maximum performance.

*  `\mint` can now take code delimited by matched curly braces `{}`.


## Availability

`minted` is distributed with both TeX Live and MiKTeX. It is also available 
from [CTAN](http://www.ctan.org/pkg/minted).  In any case, 
[Python](http://python.org/) and [Pygments](http://pygments.org/download/) 
need to be installed separately.


## License

This work may be distributed and/or modified under the conditions of the 
[LaTeX Project Public License](http://www.latex-project.org/lppl.txt) (LPPL),
version 1.3 or later.

Additionally, the project may be distributed under the terms of the 
[3-Clause ("New") BSD license](http://opensource.org/licenses/BSD-3-Clause).

Please use the project's GitHub site at <https://github.com/gpoore/minted>
for suggestions, feature requests, and bug reports.




[flattr]: https://flattr.com/submit/auto?user_id=gpoore&url=https://github.com/gpoore/minted&title=minted&category=software
