$ Simple 5x5 plate mesh for ANSA testing
$ 100mm x 100mm, 25mm element size
BEGIN BULK
$
MAT1    1       210000. .3      7.85-9
PSHELL  1       1       2.0     1
$
GRID    1               0.0     0.0     0.0
GRID    2               25.0    0.0     0.0
GRID    3               50.0    0.0     0.0
GRID    4               75.0    0.0     0.0
GRID    5               100.0   0.0     0.0
GRID    6               0.0     25.0    0.0
GRID    7               25.0    25.0    0.0
GRID    8               50.0    25.0    0.0
GRID    9               75.0    25.0    0.0
GRID    10              100.0   25.0    0.0
GRID    11              0.0     50.0    0.0
GRID    12              25.0    50.0    0.0
GRID    13              50.0    50.0    0.0
GRID    14              75.0    50.0    0.0
GRID    15              100.0   50.0    0.0
GRID    16              0.0     75.0    0.0
GRID    17              25.0    75.0    0.0
GRID    18              50.0    75.0    0.0
GRID    19              75.0    75.0    0.0
GRID    20              100.0   75.0    0.0
GRID    21              0.0     100.0   0.0
GRID    22              25.0    100.0   0.0
GRID    23              50.0    100.0   0.0
GRID    24              75.0    100.0   0.0
GRID    25              100.0   100.0   0.0
$
CQUAD4  1       1       1       2       7       6
CQUAD4  2       1       2       3       8       7
CQUAD4  3       1       3       4       9       8
CQUAD4  4       1       4       5       10      9
CQUAD4  5       1       6       7       12      11
CQUAD4  6       1       7       8       13      12
CQUAD4  7       1       8       9       14      13
CQUAD4  8       1       9       10      15      14
CQUAD4  9       1       11      12      17      16
CQUAD4  10      1       12      13      18      17
CQUAD4  11      1       13      14      19      18
CQUAD4  12      1       14      15      20      19
CQUAD4  13      1       16      17      22      21
CQUAD4  14      1       17      18      23      22
CQUAD4  15      1       18      19      24      23
CQUAD4  16      1       19      20      25      24
$
ENDDATA
