# Proposal: conditional use of locally installed Python packages

## Context

The TeX-distribution launcher for `latexminted` currently makes its adjacent
Python wheels available by prepending them to `sys.path`. This guarantees a
self-contained installation, but it also shadows packages already installed
in the interpreter's normal environment. In particular, a system installation
of Pygments (and potentially the other runtime dependencies) cannot be used
without replacing or bypassing the TeX-distribution launcher.

The reported Linux case runs `/usr/bin/latexminted` with `/bin/python3`.
The launcher therefore has an opportunity to inspect the package environment
of precisely that interpreter before changing `sys.path`.

## Desired behavior

1. Prefer the interpreter's normal import environment when it contains a
   complete, compatible installation of all runtime packages required by the
   current launcher.
2. Otherwise, retain the existing bundled-wheel behavior unchanged.
3. Do not partially mix local packages and bundled wheels. Select one
   dependency set as a unit, so imports cannot accidentally combine packages
   from different installations.
4. Preserve the launcher's current Python-version checks and all existing
   command-line behavior.

## Proposed selection algorithm

Perform dependency selection before inserting any bundled wheel into
`sys.path`:

1. Identify the runtime distributions required by the launcher:
   `latexminted`, `latexrestricted`, `latex2pydata`, and `pygments`.
2. Use `importlib.metadata` to inspect distributions visible to the running
   interpreter. Do not import the application modules merely to test
   availability; importing them could execute package code before the source
   set has been selected.
3. Require every distribution to be present and validate its installed version
   against the compatibility requirements declared by the installed
   `latexminted` distribution (including its declared runtime dependencies).
   Also validate that the installed `latexminted` version is compatible with
   the launcher version/protocol.
4. If the complete set passes, leave the normal interpreter search path
   untouched and import from the local environment.
5. If any distribution is missing, metadata is unreadable, or a version
   constraint fails, prepend the complete set of bundled wheels exactly as
   today.

The precise compatibility predicate should be derived from the project's
authoritative dependency metadata rather than duplicating version ranges in
the launcher. The launcher must handle missing or malformed distribution
metadata as a normal reason to fall back to bundled wheels, not as a fatal
startup error.

## Important implementation detail: avoid mixed environments

The current launcher inserts each wheel at the front of `sys.path`. A local
package check must therefore happen before the first such insertion. On the
local path, no bundled wheel should be added at all. On the bundled path, the
existing all-wheels-present checks and insertion order should remain intact.

This makes the selection deterministic and avoids cases where, for example,
local Pygments is combined with a bundled `latexrestricted` or vice versa.

## Security and reproducibility considerations

- The local path intentionally trusts packages installed in the interpreter's
  normal environment, just as invoking a locally installed Python application
  would. It should not add the current working directory or other new paths.
- Do not discover packages by scanning arbitrary directories or by searching
  `PATH`; use the active interpreter's standard import/distribution metadata.
- Keep bundled wheels as the fallback, preserving the current self-contained
  TeX installation behavior.
- Consider an opt-out/diagnostic environment variable only if maintainers
  identify a concrete need; it is not necessary for the first implementation.

## Tests

Add launcher-level tests for at least these cases:

- All required local distributions are present and compatible: local packages
  are selected and bundled wheels are not inserted.
- One required distribution is absent: all bundled wheels are selected.
- A local distribution has an incompatible version: all bundled wheels are
  selected.
- Distribution metadata is missing, malformed, or raises an exception:
  startup falls back cleanly to bundled wheels.
- A partial local installation never results in a mixed local/bundled set.
- Existing behavior remains unchanged when the local environment is empty.

Tests should isolate the interpreter metadata and wheel directory (for example,
with temporary package metadata and wheel fixtures), rather than depend on
packages installed on the developer's machine.

## Open questions before implementation

1. What is the launcher's authoritative compatibility contract: exact
   `latexminted` library/launcher version matching, or a supported version
   range? The implementation should follow the project's existing version
   compatibility policy.
2. Should the check require only the four direct runtime distributions, or
   validate the complete transitive dependency closure as well? The preferred
   approach is to validate the dependency closure from distribution metadata,
   while avoiding a new dependency solely for parsing metadata.
3. Should there be a diagnostic message (for example under `--debug`) that
   reports whether local or bundled packages were selected?

## Scope of this proposal

This branch records the design only. No launcher behavior is changed yet.
The next step is to inspect the Python launcher source and its packaging/test
layout, then implement the smallest testable selection helper using the
project's existing compatibility metadata.
