# Component types

## ExplicitComponent

Outputs computed directly from inputs: `outputs = f(inputs)`.

```python
class Mult(om.ExplicitComponent):
    def setup(self):
        self.add_input('x', val=0.0)
        self.add_output('y', val=0.0)
        self.declare_partials('y', 'x')         # for analytic derivatives
    def compute(self, inputs, outputs):
        outputs['y'] = 2.0 * inputs['x']
    def compute_partials(self, inputs, partials):
        partials['y', 'x'] = 2.0
```

## ImplicitComponent

Outputs satisfy a residual: `R(inputs, outputs) = 0`. Used for
governing equations not solved explicitly.

```python
class QuadResid(om.ImplicitComponent):
    def setup(self):
        self.add_input('a', val=1.0)
        self.add_output('x', val=1.0)
    def apply_nonlinear(self, inputs, outputs, residuals):
        residuals['x'] = outputs['x']**2 - inputs['a']
    def linearize(self, inputs, outputs, partials):
        partials['x', 'x'] = 2.0 * outputs['x']
        partials['x', 'a'] = -1.0
```

## ExecComp — quick formula

```python
om.ExecComp('y = 2*x + sin(z)')
om.ExecComp(['y1 = a + b', 'y2 = a*b'])         # multi-output
```

## IndepVarComp — explicit independent variables (legacy)

In modern OpenMDAO, prefer `set_input_defaults()` for promoted inputs.
`IndepVarComp` is still valid for explicitly named DVs.

## Promotes vs connect

```python
model.add_subsystem('a', X(), promotes=['x'])     # promotes 'x' to model
model.add_subsystem('b', Y(), promotes_inputs=['x'])
model.connect('a.y', 'b.input_z')                  # explicit pipe
```
