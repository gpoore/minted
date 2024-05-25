# `minted` — highlighted source code for LaTeX


## Development status

This is the development branch for `minted` version 3.0.  Beta releases are
now available.  Essentially all planned new features have been implemented
and should be usable.  However, the beta is not intended for general use.
Additional testing and security review are still needed.

The documentation in `minted.dtx` will not be updated to reflect all changes
until v3.0 is released.  Refer to `latex/CHANGELOG.md` for the current list
of changed from v2.9.

Steps for installing the current beta version:

1.  Install `minted.sty` (and `minted2.sty` if you need backward compatibility
    with v2.9).  These are located under `latex/minted/`.  To test one or both
    of these with a single document, simply download them and put them in the
    same directory (folder) with the document.  To try them with multiple
    documents, you can install them within your TeX distribution.  You could
    simply replace the existing `minted.sty`, but it will typically be better
    to put the files under `TEXMFLOCAL`, which can be located by running
    `kpsewhich --var-value TEXMFLOCAL`.  For example, you might put the files
    under `<path>/texmf-local/tex/latex/local/minted`.  Once the files are in
    place, run `texhash <TEXMFLOCAL dir>` to update TeX's index of packages.

2.  Install the new Python package with executable `latexminted`.  This is
    available from the
    [Python Package Index (PyPI)](https://pypi.org/project/latexminted/).
    For example, `python -m pip install latexminted`.  Depending on your
    system configuration, you may want `python3` instead of `python`, may need
    to add `--user`, or may need to make other modifications to the
    installation command.  It is also possible to download the Python source
    from the `python/` directory in this repository and install `latexminted`
    that way.  When `latexminted` is installed, it will also install
    `latex2pydata` and Pygments.

3.  Under Windows, an additional step is required.  The following description
    is for TeX Live; an equivalent process is needed for MiKTeX.  Within the
    TeX installation under `bin/windows/`, create a copy of `runscript.exe`
    and then rename the copy to `latexmintedwindows.exe`.  Then copy the file
    `latexmintedwindows.py` (under `latex/restricted/` in this repository) to
    `texmf-dist/scripts/minted`.  Finally, run `texhash` to update TeX's
    index.

Development of v3.0 is thanks to a
[TeX Development Fund grant](https://tug.org/tc/devfund/grants.html) from the
[TeX Users Group](https://tug.org/).



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

![screenshot](https://i.stack.imgur.com/OLUjl.png)

See the [documentation](https://github.com/gpoore/minted/blob/master/source/minted.pdf)
for examples and installation instructions.


## Availability

`minted` is distributed with both TeX Live and MiKTeX. It is also available
from [CTAN](https://www.ctan.org/pkg/minted).  In any case,
[Python](https://python.org/) and [Pygments](https://pygments.org/download/)
need to be installed separately.


## License

This work may be distributed and/or modified under the conditions of the
[LaTeX Project Public License](https://www.latex-project.org/lppl.txt) (LPPL),
version 1.3c or later.

Please use the project's GitHub site at <https://github.com/gpoore/minted>
for suggestions, feature requests, and bug reports.
