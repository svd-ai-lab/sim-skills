# Version awareness — the Step-0 probe

**Mandatory.** The first thing every task does after the session starts
is probe the runtime version and use the result to pick the right
subfolder inside the driver skill.

---

## Why this exists

A snippet written for PyFluent 0.38 (uses `.general.material`) silently
produces `AttributeError` on PyFluent 0.37 (which expects `.material`
directly). A COMSOL 6.4 API call may not exist in 6.2. Without an
explicit version check, the agent has to guess from the SDK package
version — which is exactly the failure mode this probe eliminates.

---

## The probe

After `sim connect` succeeds (persistent) — or at the start of a
one-shot task, against a short-lived session:

```bash
sim --host <host> inspect session.versions
```

Returns:

```json
{
  "sdk":                 {"name": "ansys-fluent-core", "version": "0.38.1"},
  "solver":              {"name": "fluent",            "version": "25.2"},
  "profile":             "pyfluent_0_38_modern",
  "active_sdk_layer":    "pyfluent-0.38",
  "active_solver_layer": "25.2",
  "env_path":            "/.../.sim/envs/fluent-pyfluent-0-38"
}
```

---

## How to use the result

The driver skill's `SKILL.md` tells you it has a layered folder
structure:

```
<driver>/
  base/                ← always relevant
  sdk/<slug>/          ← SDK-specific deltas (empty for SDK-less drivers)
  solver/<slug>/       ← solver-release deltas
```

Use the probe's fields to pick the right `<slug>`:

- **`base/`** — always load.
- **`sdk/<active_sdk_layer>/`** — load if set.
- **`solver/<active_solver_layer>/`** — load if set.

Later layers override earlier ones on identically-named files.

Example (Fluent):

```
active_sdk_layer = "pyfluent-0.38"  → read sdk/pyfluent-0.38/
active_solver_layer = "25.2"        → read solver/25.2/
```

If a driver skill has snippets in both `base/snippets/` and
`sdk/<slug>/snippets/`, prefer the SDK-layer snippet when it exists for
the same task — it was written against the exact API surface you're
connected to.

---

## Failure modes — stop and surface

Do **not** proceed silently if any of these hold:

- `profile` is empty or missing.
- `profile` is not listed in the driver's `compatibility.yaml`.
- `profile` is marked `deprecated` in the driver's `compatibility.yaml`.
- `active_sdk_layer` points to a directory that does not exist in the
  driver skill.

**Action**: stop, print the full `session.versions` payload, ask the
user how to proceed (upgrade, downgrade, skip).

Full contract: [`sim-cli/docs/architecture/version-compat.md`](https://github.com/svd-ai-lab/sim-cli/blob/main/docs/architecture/version-compat.md).

---

## Notes for SDK-less drivers

Some drivers (flotherm, ansa, openfoam, CLI-native OSS solvers) have no
Python SDK — they drive the solver via batch executables. For these,
`active_sdk_layer` is typically `null` and only `active_solver_layer`
(the release pin) matters. The probe shape is the same; just ignore
the null fields.
