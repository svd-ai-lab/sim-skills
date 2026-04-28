# Newton solvers

Solvers live in `newton.solvers`. The driver resolves them by class name at runtime — never hardcode the list.

| Name | Physics domain | Route A | Route B | Typical kwargs |
|---|---|---|---|---|
| `SolverXPBD` | Cloth, soft body, rigid contacts (extended position-based dynamics) | yes | yes | `iterations=10`, `rigid_contact_relaxation=0.25` |
| `SolverVBD` | Cables, rigid + deformable contacts (vertex block descent) | yes | yes | `iterations=3` |
| `SolverMuJoCo` | Articulated robots (MuJoCo-native integration) | yes | yes | `impratio`, `solimp` |
| `SolverImplicitMPM` | Granular, viscous, snow, mud (material point method) | yes | yes | `dt`, `grid_resolution` (takes a Config object) |
| `SolverStyle3D` | Garment simulation (Style3D cloth) | — | yes | (takes a Config object) |
| `SolverSemiImplicit` | Differentiable sim (autograd-friendly) | — | yes | standard |
| Custom `@wp.kernel` | User-defined physics | — | yes | n/a |

## How the driver instantiates a solver

`sim_loop._instantiate_solver` uses introspection: if the solver's `__init__` requires a `config` kwarg and the class defines a nested `Config`, kwargs are mapped onto that Config object via `setattr`. Otherwise kwargs are passed directly:

```python
# "simple" solver
solver = SolverXPBD(model, iterations=10)

# "config-style" solver
cfg = SolverImplicitMPM.Config()
cfg.dt = 0.005
solver = SolverImplicitMPM(model, config=cfg)
```

## Passing solver kwargs

Via env var (takes `key=value;key=value;...` — values coerced bool → int → float → str):

```bash
NEWTON_SOLVER_ARGS="iterations=20;enable_restitution=true" sim run recipe.json --solver newton
```

For Config-style solvers, the same syntax still works; the interpreter detects the Config shape and sets fields on the Config object.

## Step loop

The driver uses Newton's canonical step loop:

```python
for frame in range(num_frames):
    for _ in range(substeps):
        state_in.clear_forces()
        model.collide(state_in, contacts)
        solver.step(state_in, state_out, control, contacts, sim_dt)
        if hasattr(solver, "project_outside"):
            solver.project_outside(state_out, state_out, sim_dt)
        state_in, state_out = state_out, state_in
wp.synchronize()
return state_in
```

`project_outside` is only called on solvers that expose it (MPM + particle-based).
