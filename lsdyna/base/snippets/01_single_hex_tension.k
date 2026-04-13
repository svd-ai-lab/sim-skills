*KEYWORD
*TITLE
Single hex element tension test — E2E smoke test
$
$ Units: mm, ms, kg, kN, GPa
$ Steel cube 1x1x1 mm, bottom fixed, top pulled in Z
$ Expected: ~7129 cycles, normal termination in <2s
$
*CONTROL_TERMINATION
$  ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     1.0         0       0.0       0.0       0.0
*CONTROL_TIMESTEP
$  DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS      LCTM     ERODE     MS1ST
       0.0       0.9         0       0.0       0.0         0         0         0
*DATABASE_GLSTAT
$       DT
      0.01
*DATABASE_BINARY_D3PLOT
$       DT
       0.1
*NODE
       1             0.0             0.0             0.0
       2             1.0             0.0             0.0
       3             1.0             1.0             0.0
       4             0.0             1.0             0.0
       5             0.0             0.0             1.0
       6             1.0             0.0             1.0
       7             1.0             1.0             1.0
       8             0.0             1.0             1.0
*ELEMENT_SOLID
       1       1       1       2       3       4       5       6       7       8
*PART
Single hex part
$      PID     SECID       MID     EOSID      HGID      GRAV    ADPOPT      TMID
         1         1         1         0         0         0         0         0
*SECTION_SOLID
$   SECID    ELFORM       AET
         1         1         0
*MAT_ELASTIC
$      MID        RO         E        PR        DA        DB
         1  7.80E-06     210.0       0.3       0.0       0.0       0.0
*BOUNDARY_SPC_NODE
$    NID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
       1         0         1         1         1         0         0         0
       2         0         1         1         1         0         0         0
       3         0         1         1         1         0         0         0
       4         0         1         1         1         0         0         0
*LOAD_NODE_POINT
$    NID       DOF      LCID        SF       CID
       5         3         1   0.0025         0
       6         3         1   0.0025         0
       7         3         1   0.0025         0
       8         3         1   0.0025         0
*DEFINE_CURVE
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
         1         0       1.0       1.0       0.0       0.0         0
               0.000               0.000
               0.100               1.000
               1.000               1.000
*END
