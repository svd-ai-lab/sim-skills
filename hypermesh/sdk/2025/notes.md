# HyperWorks Desktop 2025 SDK Notes

## Version info

- Product: Altair HyperWorks Desktop 2025
- Python: 3.x (bundled)
- API: `import hm` (1946 model methods + 225 entity classes)
- Batch: `hw -b -script script.py`

## Key features in 2025

- Full Python 3 API replacing legacy Tcl commands
- Code Recording tool generates parametrized Python scripts
- 225 entity classes in `hm.entities`
- Collection-based entity selection (replaces Tcl marks)
- Implicit type conversion (Python lists to hwTriple/hwDoubleList/etc.)
- FilterBy classes for geometric and attribute-based selection
- AI-powered part classification (aic_* functions)

## API patterns

### Standard script structure

```python
import json
import hm
import hm.entities as ent

model = hm.Model()
hm.setoption(block_redraw=1, command_file_state=0)

def main():
    # Operations
    print(json.dumps({"ok": True, ...}))

if __name__ == "__main__":
    main()
```

### Return status checking

```python
status = model.automesh(collection=surfaces)
if status.status != 0:
    print(f"Error: {status.message}")
```

### Query pattern

```python
status, result = model.hm_getmass(collection=elements)
print(result.total_mass)
```

## Version detection

Version is embedded in install path:
`C:\Program Files\Altair\2025\hwdesktop\hw\bin\win64\hw.exe`

Or via ALTAIR_HOME environment variable.
