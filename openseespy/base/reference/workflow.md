# Standard OpenSeesPy analysis workflow

The OpenSees command sequence is **order-sensitive**. Follow this exact
order for static linear-elastic analyses; transient/nonlinear extend it
but never reorder the existing steps.

```python
import openseespy.opensees as ops

# 1. Reset state (always)
ops.wipe()

# 2. Model dimensions
ops.model('basic', '-ndm', 2, '-ndf', 3)   # 2D frame: ux, uy, rotz

# 3. Geometry: nodes
ops.node(tag, x, y[, z])

# 4. Boundary conditions: fix
ops.fix(node, ux_fix, uy_fix, rotz_fix)    # 1=fixed, 0=free; one flag per ndf

# 5. Materials (uniaxial / nDMaterial / section / fiber)
ops.uniaxialMaterial('Elastic', mat_tag, E)
# or for a beam section:
# ops.section('Elastic', sec_tag, E, A, I)

# 6. Geometric transformation (frame elements)
ops.geomTransf('Linear', transf_tag)         # or 'PDelta', 'Corotational'

# 7. Elements
ops.element('elasticBeamColumn', e_tag, n1, n2, A, E, I, transf_tag)
# truss:    ops.element('Truss', e_tag, n1, n2, A, mat_tag)

# 8. Loads: timeSeries → pattern → load
ops.timeSeries('Linear', ts_tag)
ops.pattern('Plain', pat_tag, ts_tag)
ops.load(node, Fx, Fy, Mz)                  # one term per ndf

# 9. Analysis options (THE FULL CHAIN — none optional)
ops.system('BandSPD')        # or 'BandGen', 'UmfPack', 'SparseSYM'
ops.numberer('RCM')          # or 'Plain', 'AMD'
ops.constraints('Plain')     # or 'Transformation', 'Penalty', 'Lagrange'
ops.integrator('LoadControl', dlambda)        # static
# transient: ops.integrator('Newmark', 0.5, 0.25)
ops.algorithm('Linear')      # or 'Newton', 'KrylovNewton', 'BFGS'
ops.analysis('Static')       # or 'Transient', 'VariableTransient'

# 10. Run
status = ops.analyze(N_steps)   # 0 = success, non-zero = failure
assert status == 0

# 11. Query results
u = ops.nodeDisp(node_tag, dof)        # dof: 1=ux, 2=uy, 3=rotz
r = ops.nodeReaction(node_tag, dof)
forces = ops.eleForce(ele_tag)
```

## Modal / eigen analysis

```python
# (model setup as above through step 7)
ops.system('BandGen')
ops.numberer('RCM')
ops.constraints('Plain')
ops.algorithm('Linear')
ops.analysis('Static')   # required to set up the system, even for eigen

eigs = ops.eigen(n_modes)             # returns list of eigenvalues (omega^2)
import math
periods = [2*math.pi/math.sqrt(w) for w in eigs]
```

## Time-history (ground motion)

```python
ops.timeSeries('Path', ts_tag, '-filePath', 'ag.txt', '-dt', 0.01, '-factor', 9.81)
ops.pattern('UniformExcitation', pat_tag, dir, '-accel', ts_tag)
ops.integrator('Newmark', 0.5, 0.25)
ops.algorithm('Newton')
ops.analysis('Transient')
ops.analyze(n_steps, dt)
```

## Always emit JSON for sim parse_output

```python
import json
print(json.dumps({
    "ok": status == 0,
    "tip_disp_m": ops.nodeDisp(tip, 2),
    ...
}))
```

The driver's `parse_output` reads the last JSON line.
