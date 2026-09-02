# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — native parity tests

"""Bit-exact parity between the Python floor and the native kernels.

The native module is an optional build (rust/, distribution
scpn-spheromak-native) whose Bessel functions and unit circle are the
shared kernel library's Rust crate at the pinned commit; these tests are
skipped hermetically when it is absent and compare float64 bit patterns,
never tolerances, when present. All parameter sets are synthetic fixtures.
"""

from __future__ import annotations

import pytest

from physics_fixtures import bits
from scpn_spheromak_core.physics import (
    axial_phases,
    field_sample,
    formation_disposition,
    taylor_eigenvalue,
)

native = pytest.importorskip("scpn_spheromak_native")

GEOMETRIES = [(0.5, 0.5), (0.3, 1.2), (1.0, 0.53), (0.25, 0.25)]
GRID = [
    (radius, length, fraction, index, divisions, b0)
    for radius, length in GEOMETRIES
    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0)
    for divisions in (4, 8)
    for index in range(divisions + 1)
    for b0 in (0.2, 1.5)
]


def _bits(values: tuple[float, ...]) -> list[bytes]:
    return [bits(value) for value in values]


@pytest.mark.parametrize(("radius", "length"), GEOMETRIES)
def test_eigenvalue_is_bit_exact(radius: float, length: float) -> None:
    """The wavenumbers and the eigenvalue agree bit for bit."""
    floor = taylor_eigenvalue(radius, length)
    got = native.taylor_eigenvalue(radius, length)
    assert _bits(got) == _bits(
        (
            floor.radial_wavenumber_per_m,
            floor.axial_wavenumber_per_m,
            floor.eigenvalue_per_m,
        )
    )


@pytest.mark.parametrize("divisions", [4, 8, 16])
def test_axial_phases_are_bit_exact(divisions: int) -> None:
    """Every (cos, sin) of the axial stations agrees bit for bit."""
    floor = axial_phases(divisions)
    got = native.axial_phases(divisions)
    assert len(got) == len(floor) == divisions + 1
    for (fc, fs), (gc, gs) in zip(floor, got, strict=True):
        assert _bits((gc, gs)) == _bits((fc, fs))


@pytest.mark.parametrize(
    ("radius", "length", "fraction", "index", "divisions", "b0"), GRID
)
def test_field_samples_are_bit_exact(
    radius: float, length: float, fraction: float, index: int, divisions: int, b0: float
) -> None:
    """Every component at every grid station agrees bit for bit."""
    eigen = taylor_eigenvalue(radius, length)
    cosine, sine = axial_phases(divisions)[index]
    axial = index / divisions
    floor = field_sample(fraction, axial, cosine, sine, eigen, b0)
    got = native.field_sample(fraction, axial, cosine, sine, radius, length, b0)
    assert _bits(got) == _bits(
        (
            floor.radial_fraction,
            floor.axial_fraction,
            floor.radius_m,
            floor.height_m,
            floor.radial_field_t,
            floor.azimuthal_field_t,
            floor.axial_field_t,
        )
    )


@pytest.mark.parametrize(
    ("gun", "eigenvalue", "tolerance"),
    [(12.0, 10.0, 0.1), (8.0, 10.0, 0.1), (10.5, 10.0, 0.1), (10.0, 10.0, 0.0)],
)
def test_formation_disposition_is_bit_exact(
    gun: float, eigenvalue: float, tolerance: float
) -> None:
    """The ratio agrees bit for bit and the disposition word is identical."""
    floor = formation_disposition(gun, eigenvalue, tolerance)
    got = native.formation_disposition(gun, eigenvalue, tolerance)
    assert _bits(got[:4]) == _bits(
        (
            floor.gun_lambda_per_m,
            floor.eigenvalue_per_m,
            floor.ratio,
            floor.relaxed_ratio_tolerance,
        )
    )
    assert got[4] == floor.disposition


def test_native_refusals_mirror_the_floor() -> None:
    """Every domain refusal of the bindings is a ValueError naming the field."""
    with pytest.raises(ValueError, match="radius_m"):
        native.taylor_eigenvalue(0.0, 0.5)
    with pytest.raises(ValueError, match="axial_divisions"):
        native.axial_phases(6)
    with pytest.raises(ValueError, match="radial_fraction"):
        native.field_sample(1.5, 0.0, 1.0, 0.0, 0.5, 0.5, 0.2)
    with pytest.raises(ValueError, match="axis_field_t"):
        native.field_sample(0.5, 0.0, 1.0, 0.0, 0.5, 0.5, 0.0)
    with pytest.raises(ValueError, match="relaxed_ratio_tolerance"):
        native.formation_disposition(10.0, 10.0, 1.0)
