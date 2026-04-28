# Common OpenSeesPy elements

## Truss (axial only)

```python
ops.element('Truss', tag, n1, n2, A, mat_tag)
```
- ndf=2 in 2D, ndf=3 in 3D
- requires a `uniaxialMaterial` (e.g. `'Elastic', mat_tag, E`)

## elasticBeamColumn (linear elastic frame)

2D:
```python
ops.element('elasticBeamColumn', tag, n1, n2, A, E, I, transf_tag)
```
3D:
```python
ops.element('elasticBeamColumn', tag, n1, n2, A, E, G, J, Iy, Iz, transf_tag)
```
- ndf=3 (2D) or ndf=6 (3D)
- requires a `geomTransf('Linear'|'PDelta'|'Corotational', transf_tag)` first

## forceBeamColumn (nonlinear distributed-plasticity frame)

```python
ops.section('Fiber', sec_tag); ...; # build fiber section
ops.beamIntegration('Lobatto', integ_tag, sec_tag, n_ip)
ops.element('forceBeamColumn', tag, n1, n2, transf_tag, integ_tag)
```
- For pushover / time-history with material yielding
- Slower than `elasticBeamColumn`; use only when needed

## quad (2D plane stress / plane strain)

```python
ops.element('quad', tag, n1, n2, n3, n4, thick, type_str, mat_tag)
```
- `type_str` ∈ `'PlaneStress'`, `'PlaneStrain'`
- requires `nDMaterial` (e.g. `'ElasticIsotropic'`)
- ndf=2 in 2D

## brick (3D continuum)

```python
ops.element('stdBrick', tag, n1..n8, mat_tag)
```
- 8-node hex
- requires `nDMaterial`
- ndf=3 in 3D

## ZeroLength (point spring / interface)

```python
ops.element('zeroLength', tag, n1, n2, '-mat', mat_tag, '-dir', dof)
```
- For lumped springs, contact, foundation interfaces
- `n1` and `n2` should share the same coordinates

## See also

`ops.getEleTags()`, `ops.eleType(tag)` for runtime introspection.
