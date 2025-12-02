#
# Copyright 2008,2009 Free Software Foundation, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio SDRV1 module. Place your Python package
description here (python/__init__.py).
'''

import os

try:
    from .sdrv1_python import *
except ImportError:
    dirname, filename = os.path.split(os.path.abspath(__file__))
    __path__.append(os.path.join(dirname, "bindings"))
    from .sdrv1_python import *
    
from .sdrv1_sink import sdrv1_sink
from .sdrv1_source import sdrv1_source_fc32

# Expose package version
try:
    from ._version import __version__
except Exception:
    __version__ = "0+unknown"