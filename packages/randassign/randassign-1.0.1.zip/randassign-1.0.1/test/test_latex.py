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

import randassign.latex as mdl


def test_soln_addsoln_and_cleanup():
    '''
    Test the list ``.soln``, the method ``.addsoln()``, and ``.cleanup()``.

    Along the way, this tests essentially all functionality.
    '''

    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)

        a = mdl.RandAssign()
        a.addsoln('ans')
        a.cleanup()

        fname = '_randassign.{0}.json'.format(os.path.split(__file__)[1].rsplit('.', 1)[0])
        assert os.path.isfile(fname)
        test_d = {'type': 'randassign.solutions',
                  'id': os.path.split(__file__)[1].rsplit('.', 1)[0],
                  'format': 'addsoln',
                  'solutions': [ {'info': '', 'number': 1, 'solution': ['ans']} ],
                 }
        with open(fname, encoding='utf8') as f:
            d = json.loads(f.read())
        assert test_d == d
        os.remove(fname)


        # Test cleanup with `addsoln()` with multiple solutions
        a = mdl.RandAssign()
        a.addsoln('ans1', 'ans2', info='info')
        a.addsoln('ans1', 'ans2', info='moreinfo', number=3)
        a.cleanup()

        fname = '_randassign.{0}.json'.format(os.path.split(__file__)[1].rsplit('.', 1)[0])
        assert os.path.isfile(fname)
        test_d = {'type': 'randassign.solutions',
                  'id': os.path.split(__file__)[1].rsplit('.', 1)[0],
                  'format': 'addsoln',
                  'solutions': [ {'info': 'info', 'number': 1, 'solution': ['ans1', 'ans2']},
                                 {'info': 'moreinfo', 'number': 3, 'solution': ['ans1', 'ans2']} ],
                 }
        with open(fname, encoding='utf8') as f:
            d = json.loads(f.read())
        assert test_d == d
        os.remove(fname)


        # Test cleanup with `soln.append()`
        a = mdl.RandAssign()
        a.soln.append('ans')
        a.cleanup()

        fname = '_randassign.{0}.json'.format(os.path.split(__file__)[1].rsplit('.', 1)[0])
        assert os.path.isfile(fname)
        test_d = {'type': 'randassign.solutions',
                  'id': os.path.split(__file__)[1].rsplit('.', 1)[0],
                  'format': 'soln',
                  'solutions': 'ans',
                 }
        with open(fname, encoding='utf8') as f:
            d = json.loads(f.read())
        assert test_d == d
        os.remove(fname)


        # Test error checking for using both `addsoln()` and `soln.append()`
        a = mdl.RandAssign()
        a.addsoln('ans')
        a.soln.append('ans')
        with pytest.raises(RuntimeError):
            a.cleanup()
        fname = '_randassign_soln.{0}.json'.format(os.path.split(__file__)[1].rsplit('.', 1)[0])
        assert not os.path.isfile(fname)
        a._iscleanedup = True  # Prevent atexit from actually raising the tested error at exit

        # Need to get out of temp directory so can delete it
        os.chdir(cwd)
