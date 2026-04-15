# OpenMDAO 3.x Notes

## Provenance

- Source: PyPI `openmdao`
- Verified version: 3.30.0
- Pure Python + numpy + scipy + networkx

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `om.Problem`, `om.Group` | Verified | |
| `ExplicitComponent` (setup + compute) | Verified | |
| `ExecComp('y = 2*x')` | Verified | |
| `add_subsystem(..., promotes=['*'])` | Verified | |
| `set_input_defaults` | Verified | for promoted inputs |
| `nonlinear_solver = NonlinearBlockGS()` | Verified | converges 8 iter on Sellar |
| `prob.setup() / run_model()` | Verified | |
| `prob['x']` access | Verified | post-setup |

## Sellar benchmark

`z=[5, 2], x=1` → y1=25.588, y2=12.058 (matches textbook to 5 sig figs).

## Version detection

```bash
python3 -c "import openmdao; print(openmdao.__version__)"
```
returns `3.30.0`. Driver normalizes to `3.30`.

## API differences vs older 2.x

OpenMDAO 2 (pre-2020) used `add_input` with no shape inference; current
3.x infers from `val` shape. Most 3.x examples should work unchanged
across 3.x patch releases.
