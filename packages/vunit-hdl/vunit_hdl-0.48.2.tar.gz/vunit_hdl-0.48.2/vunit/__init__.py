# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014-2015, Lars Asplund lars.anders.asplund@gmail.com

"""
Public VUnit interface
"""

from vunit.ui import VUnit
from vunit.vunit_cli import VUnitCLI
from os.path import dirname, join, abspath


# Repository root
ROOT = abspath(join(dirname(__file__), ".."))
