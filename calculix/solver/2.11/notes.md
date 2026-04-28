# CalculiX 2.11 Notes

## Provenance

- Source: Debian buster repository (`calculix-ccx_2.11-1+b3_amd64.deb`)
- Archived copy: `http://snapshot.debian.org/archive/debian/20200101T000000Z/pool/main/c/calculix-ccx/`
- Original maintainer build date: 2018-07-28

## Install layout (after `dpkg-deb -x`)

```
<prefix>/usr/bin/ccx                            # binary
<prefix>/usr/lib/x86_64-linux-gnu/libspooles.so.2.2   # solver lib
<prefix>/usr/share/doc/calculix-ccx/            # docs
```

Our install: `/data/Chenyx/sim/opt/calculix/usr/bin/ccx`
Our LD_LIBRARY_PATH: `/data/Chenyx/sim/opt/calculix/usr/lib/x86_64-linux-gnu`

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| `*STATIC` | Verified | Beam cantilever E2E passed |
| `*FREQUENCY, SOLVER=SPOOLES` | Expected | SPOOLES linked |
| `*HEAT TRANSFER` | Expected | Not yet E2E tested |
| `*NODE PRINT` → .dat | Verified | Parsed in E2E |
| `*NODE FILE` → .frd | Verified | Produced in E2E |
| B32R beam element | Verified | Used in cantilever test |

## Known limitations of 2.11 vs 2.20

- No parallelized assembly (serial stiffness matrix build)
- `SOLVER=PARDISO` unavailable (not linked)
- Contact algorithms less robust than 2.17+
- No `*RECOVER` keyword support

## Version detection

`ccx -v` prints the usage banner only (no version string). The driver
extracts "2.11" from the installation path via regex.
