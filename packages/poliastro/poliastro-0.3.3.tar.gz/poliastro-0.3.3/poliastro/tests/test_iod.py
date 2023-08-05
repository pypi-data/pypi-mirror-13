# coding: utf-8
import pytest

from numpy.testing import assert_array_almost_equal, assert_almost_equal
from astropy import units as u
from poliastro.bodies import Earth

from poliastro.iod import lambert


def test_vallado75():
    k = Earth.k
    r0 = [15945.34, 0.0, 0.0] * u.km
    r = [12214.83399, 10249.46731, 0.0] * u.km
    tof = 76.0 * u.min

    expected_va = [2.058925, 2.915956, 0.0] * u.km / u.s
    expected_vb = [-3.451569, 0.910301, 0.0] * u.km / u.s

    va, vb = lambert(k, r0, r, tof)
    assert_array_almost_equal(va.to(u.km / u.s).value,
                              expected_va.value,
                              decimal=4)
    assert_array_almost_equal(vb.to(u.km / u.s).value,
                              expected_vb.value,
                              decimal=5)


def test_curtis52():
    k = Earth.k
    r0 = [5000.0, 10000.0, 2100.0] * u.km
    r = [-14600.0, 2500.0, 7000.0] * u.km
    tof = 1.0 * u.h

    expected_va = [-5.9925, 1.9254, 3.2456] * u.km / u.s
    expected_vb = [-3.3125, -4.1966, -0.38529] * u.km / u.s

    va, vb = lambert(k, r0, r, tof)
    assert_array_almost_equal(va.to(u.km / u.s).value,
                              expected_va.value,
                              decimal=4)
    assert_array_almost_equal(vb.to(u.km / u.s).value,
                              expected_vb.value,
                              decimal=4)


def test_curtis53():
    k = Earth.k
    r0 = [273378.0, 0.0, 0.0] * u.km
    r = [145820.0, 12758.0, 0.0] * u.km
    tof = 13.5 * u.h

    # ERRATA: j component is positive
    expected_va = [-2.4356, 0.26741, 0.0] * u.km / u.s

    va, vb = lambert(k, r0, r, tof)
    assert_array_almost_equal(va.to(u.km / u.s).value,
                              expected_va.value,
                              decimal=3)
