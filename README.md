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
