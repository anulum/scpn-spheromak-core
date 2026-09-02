# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — formation disposition tests

"""The three published dispositions, the band edges and refusals."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import configuration
from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.physics import (
    DISPOSITION_HOLLOW,
    DISPOSITION_PEAKED,
    DISPOSITION_RELAXED,
    formation_disposition,
    require_ratio_tolerance,
)


def test_three_dispositions_and_band_edges() -> None:
    """Hollow above 1 + tol, peaked below 1 - tol, relaxed inside (edges inclusive)."""
    assert formation_disposition(12.0, 10.0, 0.1).disposition == DISPOSITION_HOLLOW
    assert formation_disposition(8.0, 10.0, 0.1).disposition == DISPOSITION_PEAKED
    assert formation_disposition(10.5, 10.0, 0.1).disposition == DISPOSITION_RELAXED
    assert formation_disposition(11.0, 10.0, 0.1).disposition == DISPOSITION_RELAXED
    assert formation_disposition(9.0, 10.0, 0.1).disposition == DISPOSITION_RELAXED
    assert formation_disposition(10.0, 10.0, 0.0).disposition == DISPOSITION_RELAXED
    just_above = math.nextafter(10.0, 20.0)
    assert (
        formation_disposition(just_above, 10.0, 0.0).disposition == DISPOSITION_HOLLOW
    )
    record = formation_disposition(12.0, 10.0, 0.1).to_record()
    assert record["ratio"] == 1.2
    assert set(record) == {
        "gun_lambda_per_m",
        "eigenvalue_per_m",
        "ratio",
        "relaxed_ratio_tolerance",
        "disposition",
    }


def test_zero_tolerance_peaked_side_is_the_configuration_advisory() -> None:
    """The configuration flags a source below the eigenvalue; that is 'peaked'."""
    config = configuration(bias_flux_mwb=40.0)
    gun = config.source.gun_lambda_per_m()
    conserver = config.geometry.taylor_eigenvalue_per_m()
    assert config.consistency_report()
    assert formation_disposition(gun, conserver, 0.0).disposition == DISPOSITION_PEAKED
    clean = configuration()
    assert clean.consistency_report() == ()
    disposition = formation_disposition(
        clean.source.gun_lambda_per_m(), conserver, 0.0
    ).disposition
    assert disposition == DISPOSITION_HOLLOW


@pytest.mark.parametrize(
    ("gun", "eigenvalue", "tolerance", "fragment"),
    [
        (0.0, 10.0, 0.1, "gun_lambda_per_m"),
        (10.0, 0.0, 0.1, "eigenvalue_per_m"),
        (10.0, 10.0, -0.1, "relaxed_ratio_tolerance"),
        (10.0, 10.0, 1.0, "relaxed_ratio_tolerance"),
        (10.0, 10.0, math.nan, "relaxed_ratio_tolerance"),
    ],
)
def test_refusals(
    gun: float, eigenvalue: float, tolerance: float, fragment: str
) -> None:
    """Every input is validated; nothing is clamped."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        formation_disposition(gun, eigenvalue, tolerance)
    assert require_ratio_tolerance(0.5) == 0.5
