# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device 3D model record

"""Tier-G1 device 3D model: analytic bodies of one validated design.

The model composes the validated configuration (the flux-conserver bore
and length) and the validated device geometry (conserver wall, gun
electrodes, end wall) into five named, closed, outward-oriented triangle
meshes on the device axis, regenerated deterministically from the two
records. Its canonical record carries the schema identity, the units and
axis convention, both source digests, the segment count, a summary of
every body (counts, volume, area, bounding box, mesh digest) and fixed
non-claims; the SHA-256 of that record identifies the exact model.

The meshes are analytic surfaces: the plasma body is the cylindrical
relaxed-state domain of the level-0 models (the conserver bore), not the
toroidal equilibrium shape, and no body carries an engineering property.
The gun–conserver junction is open (the gun outer electrode is contiguous
with the conserver bore, per the layout source) and no feed-through
hardware is modelled — those simplifications are properties of this tier.
The unit circle, the primitives and the mesh contract are consumed from
the pinned shared kernel library (``scpn_reactor_kernels.geometry``);
this module owns only the device composition.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_spheromak_core.configuration import DeviceConfiguration
from scpn_spheromak_core.errors import DeviceGeometryError
from scpn_spheromak_core.geometry.device import DeviceGeometry

MODEL_SCHEMA: Final = "scpn.spheromak-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the device axis, increasing from the gun to the conserver",
    "origin": "gun-side face of the flux conserver at z = 0 on the axis",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and geometry",
    "no body is an equilibrium boundary, a CAD solid or an engineering model",
    (
        "the plasma body is the cylindrical relaxed-state domain, not the "
        "toroidal equilibrium shape"
    ),
    "the gun-conserver junction and feed-through hardware are not modelled",
    "no material property, load, field or neutronic quantity is carried",
    (
        "a dimension reproduced from a published arrangement is an anchor,"
        " not a claim about that machine"
    ),
)

ROLE_ELECTRODE: Final = "electrode"
ROLE_VACUUM_BOUNDARY: Final = "vacuum_boundary"
ROLE_PLASMA: Final = "plasma"
MATERIAL_ELECTRODE_CONDUCTOR: Final = "electrode_conductor"
MATERIAL_CONSERVER_WALL: Final = "conserver_wall"
MATERIAL_PLASMA: Final = "plasma"

BODY_GUN_INNER_ELECTRODE: Final = "gun_inner_electrode"
BODY_GUN_OUTER_ELECTRODE: Final = "gun_outer_electrode"
BODY_FLUX_CONSERVER: Final = "flux_conserver"
BODY_CONSERVER_END_WALL: Final = "conserver_end_wall"
BODY_PLASMA_COLUMN: Final = "plasma_column"
BODY_NAMES: Final = (
    BODY_GUN_INNER_ELECTRODE,
    BODY_GUN_OUTER_ELECTRODE,
    BODY_FLUX_CONSERVER,
    BODY_CONSERVER_END_WALL,
    BODY_PLASMA_COLUMN,
)


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the validated configuration the model was built from.
    geometry_digest_sha256
        Digest of the validated geometry the model was built from.
    segments
        Circumferential segment count used for every body.
    meshes
        The five bodies in the fixed order of :data:`BODY_NAMES`.

    Raises
    ------
    DeviceGeometryError
        If the body names or their order differ from :data:`BODY_NAMES`.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body inventory.

        Raises
        ------
        DeviceGeometryError
            If the body names or their order differ from :data:`BODY_NAMES`.
        """
        names = tuple(mesh.name for mesh in self.meshes)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"meshes: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Schema identity, units, non-claims, source digests, segment
            count and every body summary.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "segments": self.segments,
            "bodies": [mesh.summary_record() for mesh in self.meshes],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def check_layout_invariants(
    configuration: DeviceConfiguration, geometry: DeviceGeometry
) -> None:
    """Enforce the layout invariants shared by both geometry tiers.

    The gun outer electrode is contiguous with the flux-conserver bore
    (Wood et al. 2005), so its outer radius must equal the configuration's
    conserver radius exactly.

    Parameters
    ----------
    configuration
        Validated spheromak configuration (conserver bore and length).
    geometry
        Validated device geometry.

    Raises
    ------
    DeviceGeometryError
        If the gun outer electrode's outer radius differs from the
        conserver bore radius.
    """
    outer = geometry.gun_outer_electrode_outer_radius_m
    bore = configuration.geometry.radius_m
    if outer != bore:
        raise DeviceGeometryError(
            "gun_outer_electrode_outer_radius_m: must equal the conserver bore "
            f"radius (the gun outer electrode is contiguous with the conserver), "
            f"got {outer!r} != {bore!r}"
        )


def build_device_model(
    configuration: DeviceConfiguration, geometry: DeviceGeometry, segments: int
) -> DeviceModel3D:
    """Tessellate the five bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated spheromak configuration; its conserver geometry fixes
        the bore radius and the length of the conserver and plasma bodies.
    geometry
        Validated device geometry (conserver wall, gun electrodes, end
        wall).
    segments
        Circumferential segments for every body; at least 8, multiple of 8.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid (the library's refusal is
        re-raised under the device error type with its message) or the
        layout invariants fail.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    check_layout_invariants(configuration, geometry)
    bore = configuration.geometry.radius_m
    length = configuration.geometry.length_m
    z_gun_low = 0.0 - geometry.gun_length_m
    bodies = (
        (
            BODY_GUN_INNER_ELECTRODE,
            ROLE_ELECTRODE,
            MATERIAL_ELECTRODE_CONDUCTOR,
            cylinder_solid(
                geometry.gun_inner_electrode_radius_m, z_gun_low, 0.0, segments
            ),
        ),
        (
            BODY_GUN_OUTER_ELECTRODE,
            ROLE_ELECTRODE,
            MATERIAL_ELECTRODE_CONDUCTOR,
            annular_tube(
                geometry.gun_outer_electrode_inner_radius_m,
                geometry.gun_outer_electrode_outer_radius_m,
                z_gun_low,
                0.0,
                segments,
            ),
        ),
        (
            BODY_FLUX_CONSERVER,
            ROLE_VACUUM_BOUNDARY,
            MATERIAL_CONSERVER_WALL,
            annular_tube(
                bore,
                bore + geometry.conserver_wall_thickness_m,
                0.0,
                length,
                segments,
            ),
        ),
        (
            BODY_CONSERVER_END_WALL,
            ROLE_VACUUM_BOUNDARY,
            MATERIAL_CONSERVER_WALL,
            cylinder_solid(
                bore + geometry.conserver_wall_thickness_m,
                length,
                length + geometry.end_wall_thickness_m,
                segments,
            ),
        ),
        (
            BODY_PLASMA_COLUMN,
            ROLE_PLASMA,
            MATERIAL_PLASMA,
            cylinder_solid(bore, 0.0, length, segments),
        ),
    )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        segments=segments,
        meshes=meshes,
    )
