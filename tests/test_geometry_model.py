# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device 3D model tests

"""Body inventory, placement, invariants, record identity and the pinned digest."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math

import pytest

from geometry_fixtures import (
    ANCHOR_CONSERVER_LENGTH_M,
    ANCHOR_CONSERVER_RADIUS_M,
    anchor_configuration,
    anchor_geometry,
    reference_configuration,
    reference_geometry,
)
from scpn_spheromak_core.errors import DeviceGeometryError
from scpn_spheromak_core.geometry import (
    BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    DeviceModel3D,
    build_device_model,
)

REFERENCE_MODEL_SHA256 = (
    "8b3e5c58a76f60ea7cdbea6a6baf3a7341101e3d29336d3b874cc27efd1634b4"
)


def reference_model(segments: int = 16) -> DeviceModel3D:
    """Build the reference model of these tests at a segment count."""
    return build_device_model(reference_configuration(), reference_geometry(), segments)


def test_bodies_roles_materials_and_placement() -> None:
    """Five bodies in the fixed order with the declared roles and placement."""
    configuration = reference_configuration()
    geometry = reference_geometry()
    model = reference_model()
    assert tuple(mesh.name for mesh in model.meshes) == BODY_NAMES
    assert [mesh.role for mesh in model.meshes] == [
        "electrode",
        "electrode",
        "vacuum_boundary",
        "vacuum_boundary",
        "plasma",
    ]
    assert [mesh.material_identifier for mesh in model.meshes] == [
        "electrode_conductor",
        "electrode_conductor",
        "conserver_wall",
        "conserver_wall",
        "plasma",
    ]
    inner, outer, conserver, end_wall, plasma = model.meshes
    bore = configuration.geometry.radius_m
    length = configuration.geometry.length_m
    # the gun sits below the conserver
    assert inner.bounding_box() == (
        (-geometry.gun_inner_electrode_radius_m,) * 2 + (-geometry.gun_length_m,),
        (geometry.gun_inner_electrode_radius_m,) * 2 + (0.0,),
    )
    assert outer.bounding_box()[1][2] == 0.0
    # the conserver spans z in [0, L] and [R, R + wall]
    assert conserver.bounding_box()[0][2] == 0.0
    assert conserver.bounding_box()[1][2] == length
    assert conserver.bounding_box()[1][0] == bore + geometry.conserver_wall_thickness_m
    # the end wall closes the conserver at z = L
    assert end_wall.bounding_box()[0][2] == length
    assert end_wall.bounding_box()[1][2] == length + geometry.end_wall_thickness_m
    assert end_wall.bounding_box()[1][0] == bore + geometry.conserver_wall_thickness_m
    # the plasma body is the conserver bore (the relaxed-state domain)
    assert plasma.bounding_box() == ((-bore, -bore, 0.0), (bore, bore, length))
    for mesh in model.meshes:
        assert mesh.signed_volume_m3() > 0.0


def test_volumes_follow_the_analytic_bodies() -> None:
    """Each body volume converges on the analytic cylinder or tube volume."""
    model = reference_model(1024)
    analytic = [
        math.pi * 0.05**2 * 0.3,
        math.pi * (0.4**2 - 0.38**2) * 0.3,
        math.pi * (0.42**2 - 0.4**2) * 0.6,
        math.pi * 0.42**2 * 0.02,
        math.pi * 0.4**2 * 0.6,
    ]
    for mesh, exact in zip(model.meshes, analytic, strict=True):
        assert 0.0 < (exact - mesh.signed_volume_m3()) / exact < 1.0e-5


def test_record_identity_and_pinned_digest() -> None:
    """The canonical record is sorted JSON and the reference digest is pinned."""
    configuration = reference_configuration()
    geometry = reference_geometry()
    model = build_device_model(configuration, geometry, 8)
    record = model.to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == MODEL_UNITS
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert record["configuration_digest_sha256"] == configuration.digest_sha256()
    assert record["geometry_digest_sha256"] == geometry.digest_sha256()
    assert record["segments"] == 8
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)
    data = model.canonical_bytes()
    assert json.loads(data) == record
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert model.digest_sha256() == REFERENCE_MODEL_SHA256


def test_model_is_deterministic() -> None:
    """Two builds of the same inputs are equal and share every digest."""
    first = reference_model(32)
    second = reference_model(32)
    assert first == second
    assert first.digest_sha256() == second.digest_sha256()
    assert [m.digest_sha256() for m in first.meshes] == [
        m.digest_sha256() for m in second.meshes
    ]


def test_gun_outer_electrode_must_be_contiguous_with_the_conserver() -> None:
    """A gun outer electrode not flush with the conserver bore is refused."""
    geometry = dataclasses.replace(
        reference_geometry(), gun_outer_electrode_wall_thickness_m=0.03
    )
    with pytest.raises(DeviceGeometryError, match="gun_outer_electrode_outer_radius_m"):
        build_device_model(reference_configuration(), geometry, 8)


def test_invalid_segments_are_refused_before_tessellation() -> None:
    """The segment rule is checked first."""
    with pytest.raises(DeviceGeometryError, match="multiple"):
        build_device_model(reference_configuration(), reference_geometry(), 20)


def test_body_inventory_is_enforced() -> None:
    """A model with the wrong bodies or order is refused."""
    model = reference_model(8)
    with pytest.raises(DeviceGeometryError, match="bodies must be exactly"):
        DeviceModel3D(
            configuration_digest_sha256=model.configuration_digest_sha256,
            geometry_digest_sha256=model.geometry_digest_sha256,
            segments=8,
            meshes=model.meshes[::-1],
        )


def test_model_of_the_printed_arrangement_reproduces_its_dimensions() -> None:
    """The anchor geometry reproduces every dimension the source prints.

    Wood et al. (2005) print the SSPX flux conserver as one metre in
    diameter and half a metre high. This proves the tier can carry a
    published arrangement, not that the model says anything about how that
    machine behaved.
    """
    configuration = anchor_configuration()
    model = build_device_model(configuration, anchor_geometry(), 512)
    conserver = model.meshes[2]
    assert configuration.geometry.radius_m == ANCHOR_CONSERVER_RADIUS_M
    assert configuration.geometry.length_m == ANCHOR_CONSERVER_LENGTH_M
    low, high = conserver.bounding_box()
    assert (high[0] - 0.0) * 2.0 == pytest.approx(
        2.0 * (ANCHOR_CONSERVER_RADIUS_M + anchor_geometry().conserver_wall_thickness_m)
    )
    assert (high[2] - low[2]) == ANCHOR_CONSERVER_LENGTH_M
    # the printed plasma minor/major radii are deliberately not modelled
    assert model.meshes[-1].bounding_box()[1][0] == ANCHOR_CONSERVER_RADIUS_M
    assert model.digest_sha256() != reference_model(512).digest_sha256()
