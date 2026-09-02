# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — Taylor eigenvalue tests

"""The SSPX anchor, the inverse-radius scaling and the configuration identity."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import configuration
from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.physics import (
    BESSEL_J1_FIRST_ZERO,
    conserver_eigenvalue,
    taylor_eigenvalue,
)

SSPX_PRINTED_EIGENVALUE_PER_M = 9.9
SSPX_TOLERANCE = 0.01


def test_sspx_anchor_within_declared_tolerance() -> None:
    """A 1 m diameter by 0.5 m high conserver gives 9.91 against the printed 9.9."""
    sspx = taylor_eigenvalue(0.5, 0.5)
    relative = abs(sspx.eigenvalue_per_m - SSPX_PRINTED_EIGENVALUE_PER_M)
    assert relative / SSPX_PRINTED_EIGENVALUE_PER_M < SSPX_TOLERANCE
    assert 9.90 < sspx.eigenvalue_per_m < 9.92
    assert sspx.radial_wavenumber_per_m == BESSEL_J1_FIRST_ZERO / 0.5
    assert sspx.axial_wavenumber_per_m == math.pi / 0.5
    assert set(sspx.to_record()) == {
        "radius_m",
        "length_m",
        "radial_wavenumber_per_m",
        "axial_wavenumber_per_m",
        "eigenvalue_per_m",
    }


def test_eigenvalue_is_inversely_proportional_to_the_radius_at_fixed_shape() -> None:
    """Doubling both extents halves the eigenvalue exactly (PPPL-2257)."""
    base = taylor_eigenvalue(0.5, 0.5)
    doubled = taylor_eigenvalue(1.0, 1.0)
    assert doubled.eigenvalue_per_m == base.eigenvalue_per_m / 2.0
    assert doubled.radial_wavenumber_per_m == base.radial_wavenumber_per_m / 2.0
    assert doubled.axial_wavenumber_per_m == base.axial_wavenumber_per_m / 2.0
    longer = taylor_eigenvalue(0.5, 5.0)
    assert longer.eigenvalue_per_m < base.eigenvalue_per_m
    assert longer.eigenvalue_per_m > base.radial_wavenumber_per_m


def test_configuration_identity_bit_for_bit() -> None:
    """The physics eigenvalue equals the configuration model's evaluation."""
    config = configuration()
    eigen = conserver_eigenvalue(config.geometry)
    assert eigen.eigenvalue_per_m == config.geometry.taylor_eigenvalue_per_m()
    assert eigen.radius_m == 0.5
    assert eigen.length_m == 0.5


@pytest.mark.parametrize(
    ("radius", "length", "fragment"),
    [
        (0.0, 0.5, "radius_m"),
        (0.5, -1.0, "length_m"),
        (math.nan, 0.5, "radius_m"),
        (0.5, math.inf, "length_m"),
    ],
)
def test_non_positive_extents_are_refused(
    radius: float, length: float, fragment: str
) -> None:
    """Both extents are strictly positive."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        taylor_eigenvalue(radius, length)
