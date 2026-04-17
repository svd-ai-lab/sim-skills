# Jupyter Plotting Demo (PyDyna example)

## What it demonstrates

PyDyna's `deck.plot()` method auto-detects Jupyter and uses the appropriate
PyVista backend (`static`, `server`, or `trame`). Useful for inline
geometry preview before solving.

## When to reach for this template

- Sanity-checking the geometry inside a Jupyter notebook
- Building static reports / dashboards with model previews
- Demos and tutorials

## Source

Official docs: https://dyna.docs.pyansys.com/version/stable/examples/jupyter_plotting_demo.html

## Backend choices

| Backend | Best for | Requirements |
|---------|----------|--------------|
| `static` | Notebooks rendered to HTML/PDF | Just PyVista |
| `server` | Interactive Jupyter widgets | jupyter-server-proxy |
| `trame` | Modern web-based viewer | trame (experimental) |
| `None` | Standard PyVista (desktop window) | None |

## Pattern

```python
from ansys.dyna.core import Deck, keywords as kwd
import pandas as pd

deck = Deck()
node = kwd.Node()
node.nodes = pd.DataFrame({"nid": [1,2,3,4,5,6,7,8],
                            "x": [...], "y": [...], "z": [...]})
deck.append(node)
# ... add elements, sections ...

deck.plot(jupyter_backend="static", color="lightblue", show_edges=True)
```

## Note: this is geometry preview, NOT result post-processing

For result visualization (deformation, stress contours), use **DPF**
instead — see `../pydyna_taylor_bar/README.md` for the DPF pattern.
