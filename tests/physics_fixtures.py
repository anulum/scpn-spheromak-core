# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — shared fixtures of the level-0 physics tests

"""Synthetic configurations and inputs shared by the level-0 physics tests.

Every value is a test fixture; none describes a real machine. The
"SSPX-like" flux conserver (0.5 m radius, 0.5 m length) exists only so
that the printed eigenvalue of the source can serve as an anchor.
"""

from __future__ import annotations

import struct
from typing import Any

from scpn_spheromak_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_spheromak_core.parameters import FluxConserverGeometry, FormationSource
from scpn_spheromak_core.physics import (
    LEVEL0_AXIAL_DIVISIONS,
    LEVEL0_RADIAL_STATIONS,
    ModelInputs,
)

REGISTRY_DIGEST = "786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090"


def configuration(
    radius_m: float = 0.5,
    length_m: float = 0.5,
    gun_current_ma: float = 0.2,
    bias_flux_mwb: float = 25.0,
) -> DeviceConfiguration:
    """Return a synthetic configuration with optional overrides."""
    return DeviceConfiguration(
        identifier="spheromak",
        geometry=FluxConserverGeometry(radius_m=radius_m, length_m=length_m),
        source=FormationSource(
            gun_current_ma=gun_current_ma, bias_flux_mwb=bias_flux_mwb
        ),
        external_toroidal_field_coils=False,
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def inputs(**overrides: Any) -> ModelInputs:
    """Return synthetic model inputs with optional overrides."""
    values: dict[str, Any] = {
        "axis_field_t": 0.2,
        "radial_stations": LEVEL0_RADIAL_STATIONS,
        "axial_divisions": LEVEL0_AXIAL_DIVISIONS,
        "relaxed_ratio_tolerance": 0.1,
    }
    values.update(overrides)
    return ModelInputs(**values)


def bits(value: float) -> bytes:
    """Return the IEEE-754 double bit pattern of a value."""
    return struct.pack("<d", value)
