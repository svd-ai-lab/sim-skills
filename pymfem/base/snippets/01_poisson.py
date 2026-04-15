"""Step 1: Poisson -Δu=1 on unit square (verified E2E).

Acceptance: u_max within 2% of analytical 0.073671.
Observed: 0.07353 (0.2% error) on 20x20 triangular P1 mesh.

Run: sim run 01_poisson.py --solver pymfem
"""
import json
import mfem.ser as mfem


def main():
    # Mesh
    mesh = mfem.Mesh(20, 20, "TRIANGLE", True, 1.0, 1.0)
    dim = mesh.Dimension()

    # H1 space, P1
    fec = mfem.H1_FECollection(1, dim)
    fespace = mfem.FiniteElementSpace(mesh, fec)

    # Essential BCs (all boundaries Dirichlet u=0)
    ess_tdof = mfem.intArray()
    ess_bdr = mfem.intArray([1] * mesh.bdr_attributes.Max())
    fespace.GetEssentialTrueDofs(ess_bdr, ess_tdof)

    one = mfem.ConstantCoefficient(1.0)

    # RHS
    b = mfem.LinearForm(fespace)
    b.AddDomainIntegrator(mfem.DomainLFIntegrator(one))
    b.Assemble()

    # LHS
    a = mfem.BilinearForm(fespace)
    a.AddDomainIntegrator(mfem.DiffusionIntegrator(one))
    a.Assemble()

    x = mfem.GridFunction(fespace)
    x.Assign(0.0)

    A = mfem.SparseMatrix()
    B = mfem.Vector()
    X = mfem.Vector()
    a.FormLinearSystem(ess_tdof, x, b, A, X, B)

    # Solve
    if hasattr(mfem, "UMFPackSolver"):
        solver = mfem.UMFPackSolver()
        solver.SetOperator(A)
        solver.Mult(B, X)
    else:
        M = mfem.GSSmoother(A)
        mfem.PCG(A, M, B, X, 0, 2000, 1e-12, 0.0)

    a.RecoverFEMSolution(X, b, x)

    print(json.dumps({
        "ok": True,
        "dofs": int(fespace.GetTrueVSize()),
        "u_max": float(x.GetDataArray().max()),
    }))


if __name__ == "__main__":
    main()
