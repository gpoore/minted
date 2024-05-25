# `latexminted` — Python executable for LaTeX minted package

This Python package provides a Python executable for the LaTeX
[minted](https://github.com/gpoore/minted) package.  The Python executable
performs syntax highlighting using the [Pygments](https://pygments.org/)
library.  It also provides several code formatting and manipulation features
implemented in Python that would be difficult to perform in LaTeX, such as
dedenting code and extracting code snippets from source files using regular
expressions.

The Python executable is specifically designed to be compatible with the LaTeX
security requirements for restricted shell escape executables.  These trusted
executables can run during LaTeX compilation without requiring `-shell-escape`
or similar command-line options that allow arbitrary shell commands to be
executed.
