<!-- source: https://dyna.docs.pyansys.com/version/stable/getting-started/modules/keywords.html -->

# Keywords

The `keywords` module can be used to interact with LS-DYNA keywords.

## Overview

The keywords` module of PyDyna provides Python libraries to build an Ansys LS-DYNA keyword deck.

## Usage

Here’s an example of how you can generate a *SECTION_TSHELL` keyword:

```
>>> from ansys.dyna.core.keywords import keywords
>>> shell = keywords.SectionTShell()
>>> shell
*SECTION_TSHELL
$#   secid    elform      shrf       nip     propt        qr     icomp    tshear
                   1       1.0         2       1.0         0         0         0
```

## Examples

Examples showing end-to-end workflows for using PyDyna -
write a deck using the `keywords` module and run the solver using the `run` module.

1. `Buckling_Beer_Can`
2. `John_Reid_Pendulum`
3. `John_Reid_Pipe`
4. `Taylor_Bar`
