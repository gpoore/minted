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

Notice that `minted` requires that LaTeX run with the `-shell-escape` flag.
This has security implications; it allows LaTeX to run external programs.
`-shell-escape` should only be used with documents that you trust.


## Development status

`minted` version 3.0 is now under development, thanks to a [TeX Development
Fund grant](https://tug.org/tc/devfund/grants.html) from the [TeX Users
Group](https://tug.org/).  This will bring a new Python executable that
replaces `pygmentize`.  The new executable will be compatible with restricted
shell escape, so no more `-shell-escape` with associated security
vulnerabilities.  The new executable will also make it possible to extend
`minted` using Python, not just LaTeX macros.  This will bring official
support for custom lexers, allow including snippets of external files based on
regular expressions, and make possible a number of other improvements and
bugfixes.  For compatibility purposes, the final version of `minted` v2.x will
be released as the compatibility package `minted2`.  Initial beta versions of
`minted` v3.0 are expected by early 2024.  A final minted v3.x release
including all planned features is expected before the end of summer 2024.


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
