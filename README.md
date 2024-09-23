# `minted` — highlighted source code for LaTeX


## Overview

`minted` is a LaTeX package that provides syntax highlighting using the
[Pygments](https://pygments.org/) library.  The package also provides options
for customizing the highlighted source code output, including features
implemented in Python such as selecting snippets of code with regular
expressions.

For example, this LaTeX code

```latex
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

will produce the following when compiled with LaTeX

![screenshot](https://raw.githubusercontent.com/gpoore/minted/main/readme_example.png)

See the [documentation](https://github.com/gpoore/minted/blob/main/latex/minted/minted.pdf)
for examples and installation instructions.


## Availability

`minted` is distributed with both TeX Live and MiKTeX. It is also available
from [CTAN](https://www.ctan.org/pkg/minted).


## License

This work may be distributed and/or modified under the conditions of the
[LaTeX Project Public License](https://www.latex-project.org/lppl.txt) (LPPL),
version 1.3c or later.

Please use the project's GitHub site at <https://github.com/gpoore/minted>
for suggestions, feature requests, and bug reports.
