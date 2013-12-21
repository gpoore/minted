# minted — highlighted source code for LaTeX


## Current status

`minted` was created in [2009](http://stackoverflow.com/questions/1966425/source-code-highlighting-in-latex/1985330#1985330)
by Konrad Rudolph.  Geoffrey Poore agreed to take over `minted` maintenance
in March of 2013, since his [PythonTeX](https://github.com/gpoore/pythontex)
package also provides an interface to Pygments.

`minted` is currently in final development for v2.0.  If no bugs are found in
the current alpha release, it will become v2.0 with only very minor changes.
All planned features are present in the current alpha release.  The alpha 
release should be quite stable, but users who need maximum stability are 
encouraged to use `minted` 1.7 or PythonTeX.  The release on CTAN will only 
be updated once v2.0 is finalized.


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

See the [documentation](https://github.com/gpoore/minted/source/minted.pdf)
for examples and installation instructions.


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
