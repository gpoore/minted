# minted – highlighted source code for LaTeX

`minted` is a package that facilitates expressive syntax highlighting in LaTeX
using the powerful Pygments library. The package also provides options to
customize the highlighted source code output using fancyvrb.

For instance, this code:

    :::latex
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

will produce the following rendering:

![screenshot](http://i.stack.imgur.com/OLUjl.png)

See [the documentation](https://bitbucket.org/klmr/minted/downloads/minted.pdf) for examples and instructions of installation
and usage.

## Availability

`minted` is distributed with both TeX Live and MikTeX. It is also available from [CTAN](http://www.ctan.org/tex-archive/macros/latex/contrib/minted). In any case, [Pygments](http://pygments.org/download/) needs to be installed separately. The documentation contains information on how to do that.

## License

This work may be distributed and/or modified under the conditions of the LaTeX
Project Public License, either version 1.3 of this license or (at your option)
any later version.
Additionally, the project may be distributed under the terms of the new [BSD
license](http://opensource.org/licenses/BSD-3-Clause).

For suggestions and bug reports, please go to the project’s hosting site at <https://bitbucket.org/klmr/minted>.
