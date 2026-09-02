# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — level-0 record tests

"""Composition, identity, wiring, immutability pin and refusals of the record."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math

import pytest

from physics_fixtures import configuration, inputs
from scpn_spheromak_core import (
    LEVEL0_AXIAL_DIVISIONS,
    LEVEL0_NON_CLAIMS,
    LEVEL0_RADIAL_STATIONS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0PhysicsRecord,
    ModelInputs,
    level0_physics,
)
from scpn_spheromak_core.errors import DeviceConfigurationError

REFERENCE_SHA256 = "1a068b84e22e035fbec133b33c79e1fb334fd6671d0a45b1a4f443911a9826c6"
REFERENCE_PEAKED_SHA256 = (
    "43891a13cb386f470c5eccaefa76af589c4a711c3a64dfd098d879bff13456cb"
)


def test_record_composes_every_model_and_is_canonical() -> None:
    """The record carries the digest, the eigenvalue, the disposition and the grid."""
    config = configuration()
    record = level0_physics(config, inputs())
    assert isinstance(record, Level0PhysicsRecord)
    projected = record.to_record()
    assert projected["schema"] == LEVEL0_SCHEMA
    assert projected["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert projected["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert projected["configuration_digest_sha256"] == config.digest_sha256()
    assert projected["inputs"]["radial_stations"] == list(LEVEL0_RADIAL_STATIONS)
    assert projected["inputs"]["axial_divisions"] == LEVEL0_AXIAL_DIVISIONS
    assert len(projected["field"]) == 25
    assert set(projected) == {
        "schema",
        "schema_version",
        "non_claims",
        "configuration_digest_sha256",
        "inputs",
        "eigenvalue",
        "formation",
        "field",
    }
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    assert json.loads(data) == projected
    assert record.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert level0_physics(config, inputs()).digest_sha256() == record.digest_sha256()


def test_reference_digests_are_pinned() -> None:
    """The relaxed and peaked reference records are immutability fixtures."""
    assert level0_physics(configuration(), inputs()).digest_sha256() == REFERENCE_SHA256
    peaked = level0_physics(configuration(bias_flux_mwb=40.0), inputs())
    assert peaked.digest_sha256() == REFERENCE_PEAKED_SHA256


def test_models_are_wired_to_the_configuration_and_each_other() -> None:
    """The eigenvalue is the configuration's; the field uses B0; the ratio the gun."""
    config = configuration()
    record = level0_physics(config, inputs())
    assert (
        record.eigenvalue.eigenvalue_per_m == config.geometry.taylor_eigenvalue_per_m()
    )
    assert record.formation.gun_lambda_per_m == config.source.gun_lambda_per_m()
    assert record.formation.eigenvalue_per_m == record.eigenvalue.eigenvalue_per_m
    assert record.formation.disposition == "relaxed"
    assert 1.0 < record.formation.ratio < 1.1
    hollow = level0_physics(config, inputs(relaxed_ratio_tolerance=0.0))
    assert hollow.formation.disposition == "hollow"
    midplane_axis = record.field[2]
    assert midplane_axis.radial_fraction == 0.0
    assert midplane_axis.axial_fraction == 0.5
    assert midplane_axis.axial_field_t == 0.2
    assert all(abs(s.radial_field_t) <= 1.0e-16 for s in record.field[-5:])
    peaked = level0_physics(configuration(bias_flux_mwb=40.0), inputs())
    assert peaked.formation.disposition == "peaked"
    assert peaked.formation.ratio < 0.9


def test_inputs_record_and_validation() -> None:
    """Every declared input is projected and validated."""
    model = inputs()
    assert model.to_record() == {
        "axis_field_t": 0.2,
        "radial_stations": [0.0, 0.25, 0.5, 0.75, 1.0],
        "axial_divisions": 4,
        "relaxed_ratio_tolerance": 0.1,
    }
    assert isinstance(model, ModelInputs)
    with pytest.raises(DeviceConfigurationError, match="axis_field_t"):
        dataclasses.replace(model, axis_field_t=0.0)
    with pytest.raises(DeviceConfigurationError, match="at least one station"):
        dataclasses.replace(model, radial_stations=())
    with pytest.raises(DeviceConfigurationError, match=r"radial_stations\[1\]"):
        dataclasses.replace(model, radial_stations=(0.0, 1.5))
    with pytest.raises(DeviceConfigurationError, match=r"radial_stations\[0\]"):
        dataclasses.replace(model, radial_stations=(math.nan, 1.0))
    with pytest.raises(DeviceConfigurationError, match="strictly increasing"):
        dataclasses.replace(model, radial_stations=(0.5, 0.5))
    with pytest.raises(DeviceConfigurationError, match="axial_divisions"):
        dataclasses.replace(model, axial_divisions=6)
    with pytest.raises(DeviceConfigurationError, match="relaxed_ratio_tolerance"):
        dataclasses.replace(model, relaxed_ratio_tolerance=1.0)
    assert dataclasses.replace(model, radial_stations=(0.3,)).radial_stations == (0.3,)
