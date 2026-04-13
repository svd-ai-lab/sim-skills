# VMFL015 — Working Fluid Pipe Flow

## Case description

| Property | Value |
|----------|-------|
| **Case ID** | VMFL015_CFX |
| **Physics** | Incompressible pipe flow |
| **Material** | Working Fluid (custom: ρ=894 kg/m³, μ=0.00153 Pa·s) |
| **Turbulence** | SST (k-ω Shear Stress Transport) |
| **Inlet** | Mass flow rate: 1.379 kg/s |
| **Outlet** | Opening, 0 Pa gauge |
| **Temperature** | Isothermal, 25°C |
| **Iterations** | Max 200, target RMS < 1e-5 |

## Execution

```bash
# Step 1: Solve
cfx5solve -batch -def 015.def

# Step 2: Post-process
cfx5post -batch post_process.cse 015_002.res

# Step 3: Export convergence data
cfx5mondata -res 015_002.res -out convergence.csv
```

## Results (observed on Ansys 24.1)

| Metric | Value |
|--------|-------|
| Iterations to converge | 122 |
| Wall clock time | 374.8 s |
| U-Mom RMS | 8.9e-6 |
| V-Mom RMS | 6.7e-6 |
| W-Mom RMS | 9.9e-6 |
| P-Mass RMS | 4.8e-7 |

All residuals converged below the 1e-5 target. Solve reached steady state with interrupt control triggering at iteration 122.

## Evidence

| File | Description |
|------|-------------|
| `evidence/pressure_contour.png` | Pressure distribution on pipe walls |
| `evidence/velocity_contour.png` | Velocity magnitude on pipe walls |
| `evidence/e2e_summary.json` | Machine-readable test summary |

## Acceptance criteria

1. All RMS residuals < 1e-5 (target)
2. Convergence within 200 iterations
3. `.res` file > 1 MB (contains full field data)
4. Pressure contour shows expected inlet-high / outlet-low pattern
5. Velocity contour shows uniform pipe flow profile
