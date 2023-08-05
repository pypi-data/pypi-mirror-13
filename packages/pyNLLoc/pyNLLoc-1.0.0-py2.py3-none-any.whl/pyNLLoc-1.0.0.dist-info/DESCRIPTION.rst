Python module for running NonLinLoc, including on a cluster, as well as providing utilities for converting location scatter files into angle distributions.

Code by David J Pugh


# pyNLLoc

This is a Python module for running NonLinLoc, including on a cluster, as well as providing utilities for converting location scatter files into angle distributions. The angle conversion utilities, Scat2Angle and XYZ2Angle require the C++ program, GetNLLOCScatterAngles to be compiled.

This module provides
    pyNLLoc - Rrunning NLLoc using python
    Scat2Angle - Convert location scatter distribution to angle distribution
    XYZ2Angle - Calculates the angles for given x, y, z coordinates

# Compiling GetNLLOCScatterAngles

GetNLLOCScatterAngles is compiled from source, either using the makefile or the script make_angles.sh.

This compiles the GetAngles.cpp file, which is dependent on some NonLinLoc files, these are included in the 
folder NLLoc_code, but it is equally possible to use another NLLoc source directory by setting the 
NLLOC_PATH in the makefile (or script). It is recommended to use the latest NLLoc source code, but it is 
important to note that as of 17/12/2015 Version 6.00 has a bug in GridLib.c related to angle interpolation,
so a fixed versin of GridLib.c is provided in the pyNLLoc distribution. This is fixed as of 2013\08\23 in beta version, but may not be fixed in the latest release.



--------------------------------------------------------------------------
Written by David J Pugh <david.j.pugh@cantab.net>



