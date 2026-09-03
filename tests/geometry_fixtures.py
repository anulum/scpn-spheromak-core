# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — shared fixtures of the geometry tests

"""Configurations and geometries shared by the geometry tests.

Two fixtures, and the difference between them is the point.

The *reference* pair is synthetic: round numbers chosen to exercise the
model, describing no machine.

The *anchor* pair carries the flux-conserver dimensions printed by Wood
et al., "Improved operation of the SSPX spheromak", UCRL-JRNL-214703
(2005), already on file: a conserver one metre in diameter and half a
metre high. It exists so the geometry tier can be checked against a
published arrangement the way the level-0 models are checked against
published numbers (the same printed values anchor the level-0 Taylor
eigenvalue). The fields the source does not print — the wall thicknesses,
the gun radii and the gun length — are declared here and marked as
declared; reproducing a printed dimension is an anchor, never a claim
about that machine.
"""

from __future__ import annotations

import struct

from scpn_spheromak_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_spheromak_core.geometry import DeviceGeometry
from scpn_spheromak_core.parameters import FluxConserverGeometry, FormationSource

REGISTRY_DIGEST = "786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090"


def reference_configuration() -> DeviceConfiguration:
    """Return the synthetic spheromak configuration of these tests."""
    return DeviceConfiguration(
        identifier="spheromak",
        geometry=FluxConserverGeometry(radius_m=0.4, length_m=0.6),
        source=FormationSource(gun_current_ma=0.5, bias_flux_mwb=5.0),
        external_toroidal_field_coils=False,
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def reference_geometry() -> DeviceGeometry:
    """Return the synthetic spheromak geometry of these tests."""
    return DeviceGeometry(
        conserver_wall_thickness_m=0.02,
        gun_inner_electrode_radius_m=0.05,
        gun_outer_electrode_inner_radius_m=0.38,
        gun_outer_electrode_wall_thickness_m=0.02,
        gun_length_m=0.3,
        end_wall_thickness_m=0.02,
    )


#: Values printed by Wood et al. (2005) for the SSPX flux conserver.
ANCHOR_CONSERVER_RADIUS_M = 0.5
ANCHOR_CONSERVER_LENGTH_M = 0.5


def anchor_configuration() -> DeviceConfiguration:
    """Return the configuration of the printed SSPX flux conserver.

    The conserver bore radius and length are the printed values; the
    formation-source parameters are declared, and do not enter the
    geometry.
    """
    return DeviceConfiguration(
        identifier="spheromak",
        geometry=FluxConserverGeometry(
            radius_m=ANCHOR_CONSERVER_RADIUS_M,
            length_m=ANCHOR_CONSERVER_LENGTH_M,
        ),
        source=FormationSource(gun_current_ma=0.5, bias_flux_mwb=5.0),
        external_toroidal_field_coils=False,
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def anchor_geometry() -> DeviceGeometry:
    """Return the geometry of the printed SSPX flux conserver.

    Every value is declared: the source prints the conserver's bore and
    height (which live in the configuration), not the wall, gun or end-wall
    dimensions.
    """
    return DeviceGeometry(
        conserver_wall_thickness_m=0.02,
        gun_inner_electrode_radius_m=0.05,
        gun_outer_electrode_inner_radius_m=0.48,
        gun_outer_electrode_wall_thickness_m=0.02,
        gun_length_m=0.3,
        end_wall_thickness_m=0.02,
    )


def bits(value: float) -> bytes:
    """Return the IEEE-754 double bit pattern of a value."""
    return struct.pack("<d", value)


def stream_bits(values: list[float]) -> bytes:
    """Return the concatenated bit patterns of a float stream."""
    return b"".join(bits(value) for value in values)
