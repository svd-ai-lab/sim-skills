$
$ANSA_VERSION;25.0.0;
$
$
$ file created by  A N S A  Fri Apr  3 21:22:00 2026
$
$ output from :
$
$ E:/sim/sim-agent-ansa/Untitled
$
$ Settings :
$
$ Output format : MSC Nastran
$
$ Output : Visible
$
$
$
$
BEGIN BULK                                                                      
GRID           1              0.      0.      0.
GRID           2             25.      0.      0.
GRID           3             50.      0.      0.
GRID           4             75.      0.      0.
GRID           5            100.      0.      0.
GRID           6              0.     25.      0.
GRID           7             25.     25.      0.
GRID           8             50.     25.      0.
GRID           9             75.     25.      0.
GRID          10            100.     25.      0.
GRID          11              0.     50.      0.
GRID          12             25.     50.      0.
GRID          13             50.     50.      0.
GRID          14             75.     50.      0.
GRID          15            100.     50.      0.
GRID          16              0.     75.      0.
GRID          17             25.     75.      0.
GRID          18             50.     75.      0.
GRID          19             75.     75.      0.
GRID          20            100.     75.      0.
GRID          21              0.    100.      0.
GRID          22             25.    100.      0.
GRID          23             50.    100.      0.
GRID          24             75.    100.      0.
GRID          25            100.    100.      0.
CQUAD4         1       1       1       2       7       6
CQUAD4         2       1       2       3       8       7
CQUAD4         3       1       3       4       9       8
CQUAD4         4       1       4       5      10       9
CQUAD4         5       1       6       7      12      11
CQUAD4         6       1       7       8      13      12
CQUAD4         7       1       8       9      14      13
CQUAD4         8       1       9      10      15      14
CQUAD4         9       1      11      12      17      16
CQUAD4        10       1      12      13      18      17
CQUAD4        11       1      13      14      19      18
CQUAD4        12       1      14      15      20      19
CQUAD4        13       1      16      17      22      21
CQUAD4        14       1      17      18      23      22
CQUAD4        15       1      18      19      24      23
CQUAD4        16       1      19      20      25      24
PSHELL         1       1      3.       1
MAT1           1 210000.     0.3  7.85-9
$ANSA_COLOR;1;PSHELL;.952941179275513;.874509811401367;.105882354080677;1.;
$ANSA_COLOR;1;MAT1;.560784339904785;.556862771511078;.517647087574005;1.;
$ANSA_NAME_COMMENT;1;MAT1;Default MAT1;;NO;NO;NO;
$ANSA_NAME_COMMENT;1;PSHELL;PSHELL Property Card;;NO;NO;NO;NO;
$ANSA_USER_ATTRIBUTES;PSHELL;User/cad_material;TEXT;RW;YES;;;
$ANSA_USER_ATTRIBUTES;PSHELL;User/cad_thickness;TEXT;RW;YES;;;
$ANSA_PART;GROUP;ID;2;NAME;input_plate.nas;BELONGS_HERE;YES;PID_OFFSET;0;COLOR;2
$03;202;97;0;IS_COLOR_ACTIVE;-1;PART_TYPE;Undefined;ATTRIBUTES;2;DM/File Type;AN
$SA;DM/Status;WIP;CONTAINS;ANSAPART;4;
$ANSA_PART;PART;ID;4;MID;1;NAME;1 PSHELL Property Card;BELONGS_HERE;YES;STUDY_VE
$RSION;0;PID_OFFSET;0;COLOR;208;134;56;0;IS_COLOR_ACTIVE;-1;PART_TYPE;Undefined;
$ATTRIBUTES;2;DM/File Type;ANSA;DM/Status;WIP;CONTAINS;PSHELL;1;
ENDDATA
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
