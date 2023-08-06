#
# Copyright 2015 Universidad Complutense de Madrid
#
# This file is part of Numina
#
# Numina is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Numina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Numina.  If not, see <http://www.gnu.org/licenses/>.
#

'''Unit test for trace'''

from __future__ import division

import pytest
import numpy as np
from numpy.testing import assert_allclose

from ..traces import trace
from ..traces import axis_to_dispaxis

def test_axis_to_dispaxis():

    assert axis_to_dispaxis(0) == 1
    assert axis_to_dispaxis(1) == 0

    with pytest.raises(ValueError):
        axis_to_dispaxis(2)
        

def test_trace_simple():
    '''Trace doesn't work with a flat peak'''
    arr = np.zeros((100, 100))

    arr[47,45:55] = 10.0
    arr[48,45:55] = 100.0
    arr[49,45:55] = 12.0

    result = np.empty((12, 3))
    result[:,0] = np.arange(44, 56)
    result[:,1] = 48.0056179775
    result[4, 1] = 48.0
    result[:,2] = 100.00280898876404
    result[[0, 11], 2] = 33.33426966
    result[[1,10], 2] = 66.66853933
    result[4, 2] = 100.0

    mm = trace(arr, 48.0, 48.0, step=1)

    assert mm.shape == (12, 3)
    assert_allclose(mm, result)


def test_trace_bug_27():
    '''Trace doesn't work with a flat peak'''
    arr = np.zeros((100, 100))
    arr[47:52,12:90] = 100.0
    mm = trace(arr, 50, 50)
    assert mm.shape[0] >= 1
