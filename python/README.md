# `latexminted` — Python executable for LaTeX minted package

This Python package provides the Python side of the LaTeX
[`minted`](https://github.com/gpoore/minted) package.  It performs syntax
highlighting using the [Pygments](https://pygments.org/) library.  It also
provides several code formatting and manipulation features implemented in
Python that would be difficult to perform in LaTeX, such as dedenting code and
extracting code snippets from source files using regular expressions.

This package should only be installed manually if you need to use plugin
packages for Pygments.  The package is bundled within TeX distributions as a
Python wheel along with the LaTeX `minted` package.  Installing the LaTeX
`minted` package with your TeX distribution's package manager will also
install the `latexminted` Python package and all required Python libraries
within the TeX installation.  If you do need Pygments plugins, then install
`latexminted` manually along with Pygments in a Python installation.  Make
sure that the `latexminted` executable that is created as part of this process
has precedence on `PATH` over the `latexminted` executable in your TeX
installation.  For Windows, precedence on either the system `PATH` or the user
`PATH` is usually sufficient, as long as the TeX installation is in a typical
location and any user Python executable is within a Python installation under
the user's home directory.

This Python package is specifically designed to be compatible with the LaTeX
security requirements for restricted shell escape executables.  These trusted
executables can run during LaTeX compilation without requiring `-shell-escape`
or similar command-line options that allow arbitrary shell commands to be
executed.
