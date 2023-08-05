# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os
import sys
if sys.version_info.major == 2:
    from io import open
import pytest
import json
import atexit
import tempfile

import randassign.make as mdl
