"""
PyFeyn - a simple Python interface for making Feynman diagrams.
"""

__author__ = "Andy Buckley & Georg von Hippel (pyfeyn at projects.hepforge.org)"
__version__ = "1.0.0"
__date__ = "$Date: 2016-02-09 22:19:36 +0000 (Tue, 09 Feb 2016) $"
__copyright__ = "Copyright (c) 2007-2016 Andy Buckley, Georg von Hippel, George Williams"
__license__ = "GPL"

## Set __all__ (for "from pyfeyn import *")
__all__ = ["diagrams", "points", "blobs", "lines", "deco", "utils", "config"]

## Import PyX and set up some things
try:
    import pyx
except:
    print("You don't have PyX - that's a problem unless you're just running the setup script.")
    import sys
    sys.exit()

## Check the version
from distutils.version import StrictVersion as Version
pyxversion = Version(pyx.version.version)
if pyxversion < Version("0.9.0"):
    print("Warning: PyFeyn may not work with PyX versions older than 0.9!")

## Units
pyx.unit.set(uscale = 4, vscale = 4, wscale = 4, xscale = 4)
pyx.unit.set(defaultunit = "cm")

## TeX stuff
if pyxversion >= Version("0.13.0"):
    pyx.text.set(pyx.text.LatexRunner)
else:
    pyx.text.defaulttexrunner.set(mode="latex")

import subprocess
try:
  subprocess.Popen(["kpsewhich","hepnicenames.sty"])
  if pyxversion >= Version("0.13.0"):
    pyx.text.default_runner.preamble(r"\usepackage{hepnicenames}")
  else:
    pyx.text.defaulttexrunner.preamble(r"\usepackage{hepnicenames}")
except:
  print("Warning: hepnicenames package not found!")
