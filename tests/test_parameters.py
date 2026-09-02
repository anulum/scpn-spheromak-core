# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — parameter model tests

"""Every validation branch of the spheromak parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math

import pytest

from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import (
    BESSEL_J1_FIRST_ZERO,
    MU0,
    FluxConserverGeometry,
    FormationSource,
    require_finite,
    require_positive,
)


def synthetic_geometry(**overrides: float) -> FluxConserverGeometry:
    """Build a valid synthetic flux conserver with optional overrides."""
    values: dict[str, float] = {"radius_m": 0.5, "length_m": 1.0}
    values.update(overrides)
    return FluxConserverGeometry(**values)


def synthetic_source(**overrides: float) -> FormationSource:
    """Build a valid synthetic formation source with optional overrides."""
    values: dict[str, float] = {"gun_current_ma": 0.1, "bias_flux_mwb": 15.0}
    values.update(overrides)
    return FormationSource(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_taylor_eigenvalue_formula() -> None:
    """The conserver eigenvalue follows the cylindrical Taylor formula exactly."""
    value = synthetic_geometry().taylor_eigenvalue_per_m()
    radial = BESSEL_J1_FIRST_ZERO / 0.5
    axial = math.pi / 1.0
    assert value == math.sqrt(radial * radial + axial * axial)
    assert value == pytest.approx(math.sqrt((3.832 / 0.5) ** 2 + math.pi**2), rel=1e-4)
    assert BESSEL_J1_FIRST_ZERO == 3.8317059702075125
    assert round(BESSEL_J1_FIRST_ZERO, 3) == 3.832


def test_gun_lambda_formula() -> None:
    """The source parameter follows ``mu0 I / Phi`` exactly."""
    value = synthetic_source().gun_lambda_per_m()
    expected = MU0 * 0.1e6 / 15.0e-3
    assert value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"radius_m": 0.0}, "radius_m"),
        ({"radius_m": -1.0}, "radius_m"),
        ({"length_m": 0.0}, "length_m"),
        ({"length_m": math.nan}, "length_m"),
    ],
)
def test_invalid_geometry_is_rejected(
    overrides: dict[str, float], fragment: str
) -> None:
    """Each flux-conserver violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_geometry(**overrides)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"gun_current_ma": 0.0}, "gun_current_ma"),
        ({"gun_current_ma": math.inf}, "gun_current_ma"),
        ({"bias_flux_mwb": 0.0}, "bias_flux_mwb"),
        ({"bias_flux_mwb": -5.0}, "bias_flux_mwb"),
    ],
)
def test_invalid_source_is_rejected(overrides: dict[str, float], fragment: str) -> None:
    """Each formation-source violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_source(**overrides)
