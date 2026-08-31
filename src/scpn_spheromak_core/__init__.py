# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device configuration model package

"""Device configuration model of the SCPN spheromak device family.

Public surface of the ``device_configuration_model`` capability at
``computational_prototype`` maturity: validated parameter objects,
documented consistency estimates, canonical serialisation with SHA-256
digests, and a data-only pin to the SPO reactor registry. No claim about
any real machine is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_spheromak_core.configuration import (
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import (
    BESSEL_J1_FIRST_ZERO,
    MU0,
    FluxConserverGeometry,
    FormationSource,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "BESSEL_J1_FIRST_ZERO",
    "MU0",
    "OWNED_CONFIGURATIONS",
    "ConsistencyFinding",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "FluxConserverGeometry",
    "FormationSource",
    "RegistryBinding",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
]
