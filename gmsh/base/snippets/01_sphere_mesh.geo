// Step 1: Unit sphere 3D mesh (verified E2E)
// Acceptance: 100 < nodes < 2000, 300 < elements < 5000, bbox ~ ±1
//
// Run: sim run 01_sphere_mesh.geo --solver gmsh
// Output: sphere.msh (MSH 2.2 format)
//
SetFactory("OpenCASCADE");
Sphere(1) = {0, 0, 0, 1.0};
Physical Volume("ball") = {1};
Physical Surface("surf") = {1};
Mesh.MeshSizeMax = 0.3;
