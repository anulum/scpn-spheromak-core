# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — relaxed-state field tests

"""Boundary conditions, the axis, the curl identity and the grid layout."""

from __future__ import annotations

import math

import pytest

from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.physics import (
    AXIAL_DIVISION_MULTIPLE,
    MIN_AXIAL_DIVISIONS,
    FieldSample,
    axial_phases,
    field_grid,
    field_sample,
    require_axial_divisions,
    require_radial_station,
    taylor_eigenvalue,
)

EIGEN = taylor_eigenvalue(0.5, 0.5)
B0 = 0.2


def test_axial_phases_are_the_unit_circle_at_multiples_of_pi_over_n() -> None:
    """(cos, sin) of pi k / N for k = 0..N; exact at the plates and the midplane."""
    phases = axial_phases(4)
    assert len(phases) == 5
    assert phases[0] == (1.0, 0.0)
    assert phases[2] == (0.0, 1.0)
    assert phases[4] == (-1.0, 0.0)
    for index, (cosine, sine) in enumerate(phases):
        assert math.isclose(cosine, math.cos(math.pi * index / 4), abs_tol=1.0e-15)
        assert math.isclose(sine, math.sin(math.pi * index / 4), abs_tol=1.0e-15)
    assert len(axial_phases(8)) == 9
    assert require_axial_divisions(MIN_AXIAL_DIVISIONS) == 4
    assert AXIAL_DIVISION_MULTIPLE == 4


@pytest.mark.parametrize("divisions", [0, 2, 3, 5, 6, 7, 9, True])
def test_invalid_axial_divisions_are_refused(divisions: int) -> None:
    """N is at least four and a multiple of four."""
    with pytest.raises(DeviceConfigurationError, match="axial_divisions"):
        require_axial_divisions(divisions)
    with pytest.raises(DeviceConfigurationError, match="axial_divisions"):
        axial_phases(divisions)


def test_midplane_axis_carries_b0_and_no_other_component() -> None:
    """At r = 0, z = L/2: B_z = B0 exactly, B_r = B_theta = 0."""
    cosine, sine = axial_phases(4)[2]
    axis = field_sample(0.0, 0.5, cosine, sine, EIGEN, B0)
    assert isinstance(axis, FieldSample)
    assert axis.axial_field_t == B0
    assert axis.azimuthal_field_t == 0.0
    assert axis.radial_field_t == 0.0
    assert axis.radius_m == 0.0
    assert axis.height_m == 0.25
    assert set(axis.to_record()) == {
        "radial_fraction",
        "axial_fraction",
        "radius_m",
        "height_m",
        "radial_field_t",
        "azimuthal_field_t",
        "axial_field_t",
    }


def test_conducting_wall_and_end_plates() -> None:
    """B_r(R, z) vanishes to the kernel's zero; B_z(r, 0) = B_z(r, L) = 0 exactly."""
    for cosine, sine in axial_phases(4):
        wall = field_sample(1.0, 0.0, cosine, sine, EIGEN, B0)
        assert abs(wall.radial_field_t) <= 1.0e-15 * B0
        assert abs(wall.azimuthal_field_t) <= 1.0e-15 * B0
    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        bottom = field_sample(fraction, 0.0, *axial_phases(4)[0], EIGEN, B0)
        top = field_sample(fraction, 1.0, *axial_phases(4)[4], EIGEN, B0)
        assert bottom.axial_field_t == 0.0
        assert top.axial_field_t == 0.0
        assert bottom.azimuthal_field_t == 0.0
        assert top.radial_field_t == -bottom.radial_field_t


def test_field_satisfies_curl_b_equals_lambda_b_by_finite_differences() -> None:
    """The three components of curl B equal lambda B to 1e-6 (central differences)."""
    k_r = EIGEN.radial_wavenumber_per_m
    k_z = EIGEN.axial_wavenumber_per_m
    lam = EIGEN.eigenvalue_per_m

    def field(r: float, z: float) -> tuple[float, float, float]:
        from scpn_spheromak_core.physics import bessel_j0, bessel_j1

        j0 = bessel_j0(k_r * r)
        j1 = bessel_j1(k_r * r)
        return (
            -B0 * (k_z / k_r) * j1 * math.cos(k_z * z),
            B0 * (lam / k_r) * j1 * math.sin(k_z * z),
            B0 * j0 * math.sin(k_z * z),
        )

    r, z, h = 0.2, 0.15, 1.0e-5
    b_r, b_t, b_z = field(r, z)
    d_br_dz = (field(r, z + h)[0] - field(r, z - h)[0]) / (2.0 * h)
    d_bz_dr = (field(r + h, z)[2] - field(r - h, z)[2]) / (2.0 * h)
    d_bt_dz = (field(r, z + h)[1] - field(r, z - h)[1]) / (2.0 * h)
    d_rbt_dr = ((r + h) * field(r + h, z)[1] - (r - h) * field(r - h, z)[1]) / (2.0 * h)
    d_rbr_dr = ((r + h) * field(r + h, z)[0] - (r - h) * field(r - h, z)[0]) / (2.0 * h)
    assert math.isclose(-d_bt_dz, lam * b_r, rel_tol=1.0e-6)
    assert math.isclose(d_br_dz - d_bz_dr, lam * b_t, rel_tol=1.0e-6)
    assert math.isclose(d_rbt_dr / r, lam * b_z, rel_tol=1.0e-6)
    divergence = d_rbr_dr / r + (field(r, z + h)[2] - field(r, z - h)[2]) / (2.0 * h)
    assert abs(divergence) <= 1.0e-6 * lam * B0


def test_grid_layout_and_station_refusals() -> None:
    """Radial stations outermost, axial innermost; stations outside [0, 1] refused."""
    grid = field_grid(EIGEN, B0, (0.0, 1.0), 4)
    assert len(grid) == 10
    assert [s.radial_fraction for s in grid[:5]] == [0.0] * 5
    assert [s.axial_fraction for s in grid[:5]] == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert grid[5].radial_fraction == 1.0
    assert field_grid(EIGEN, B0, (), 4) == ()
    for bad in (-0.1, 1.1, math.nan):
        with pytest.raises(DeviceConfigurationError, match="radial_fraction"):
            field_sample(bad, 0.0, 1.0, 0.0, EIGEN, B0)
        with pytest.raises(DeviceConfigurationError, match="station"):
            require_radial_station("station", bad)
    with pytest.raises(DeviceConfigurationError, match="axis_field_t"):
        field_sample(0.5, 0.0, 1.0, 0.0, EIGEN, 0.0)
    assert require_radial_station("station", 1.0) == 1.0
