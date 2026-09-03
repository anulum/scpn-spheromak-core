# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — level-0 physics record

"""Level-0 physics record of one validated spheromak configuration.

The record composes the cylindrical Taylor eigenvalue of the flux
conserver, the formation disposition of the declared source, and the
Chandrasekhar–Kendall field of the relaxed state on a declared grid, on
the validated :class:`~scpn_spheromak_core.configuration.DeviceConfiguration`
together with the declared model inputs the configuration does not carry.
It serialises canonically with a SHA-256 digest and states its own
non-claims: every number is a closed-form evaluation on a synthetic
configuration, at ``computational_prototype`` maturity; no equation is
solved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_spheromak_core.configuration import DeviceConfiguration
from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import require_positive
from scpn_spheromak_core.physics.eigenvalue import (
    TaylorEigenvalue,
    conserver_eigenvalue,
)
from scpn_spheromak_core.physics.field import (
    FieldSample,
    field_grid,
    require_axial_divisions,
    require_radial_station,
)
from scpn_spheromak_core.physics.formation import (
    FormationDisposition,
    formation_disposition,
    require_ratio_tolerance,
)

LEVEL0_SCHEMA: Final = "scpn.spheromak-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
#: The plan's radial stations ``r / R``.
LEVEL0_RADIAL_STATIONS: Final = (0.0, 0.25, 0.5, 0.75, 1.0)
#: The plan's axial divisions (stations ``z / L`` at quarters).
LEVEL0_AXIAL_DIVISIONS: Final = 4
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of the lowest axisymmetric relaxed state of an "
        "ideal cylindrical flux conserver on a synthetic configuration"
    ),
    (
        "no equation is solved: no equilibrium reconstruction, no stability, "
        "confinement, helicity-balance or resistive-decay calculation"
    ),
    (
        "the formation disposition restates a published operating rule of thumb "
        "against a declared tolerance; it predicts nothing"
    ),
    (
        "no value describes or validates any real machine; the eigenvalue anchor "
        "reproduces one printed number within its declared tolerance"
    ),
)


@dataclass(frozen=True, slots=True)
class ModelInputs:
    """Declared inputs of the level-0 models beyond the configuration.

    Parameters
    ----------
    axis_field_t
        ``B0``, the axial field on the axis at the midplane; strictly
        positive.
    radial_stations
        Normalised radii ``r / R``; non-empty, each within ``[0, 1]``,
        strictly increasing.
    axial_divisions
        ``N``; the axial stations are ``k / N`` for ``k = 0 .. N``; at
        least four and a multiple of four.
    relaxed_ratio_tolerance
        Half-width of the relaxed band of the formation disposition in
        ``[0, 1)``.

    Raises
    ------
    DeviceConfigurationError
        If any input is invalid.
    """

    axis_field_t: float
    radial_stations: tuple[float, ...]
    axial_divisions: int
    relaxed_ratio_tolerance: float

    def __post_init__(self) -> None:
        """Validate every declared input.

        Raises
        ------
        DeviceConfigurationError
            If any input is invalid.
        """
        require_positive("axis_field_t", self.axis_field_t)
        if not self.radial_stations:
            raise DeviceConfigurationError(
                "radial_stations: at least one station is required"
            )
        for index, fraction in enumerate(self.radial_stations):
            require_radial_station(f"radial_stations[{index}]", fraction)
        if any(
            later <= earlier
            for earlier, later in zip(
                self.radial_stations, self.radial_stations[1:], strict=False
            )
        ):
            raise DeviceConfigurationError(
                "radial_stations: must be strictly increasing, got "
                f"{self.radial_stations!r}"
            )
        require_axial_divisions(self.axial_divisions)
        require_ratio_tolerance(self.relaxed_ratio_tolerance)

    def to_record(self) -> dict[str, Any]:
        """Project the inputs to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "axis_field_t": self.axis_field_t,
            "radial_stations": list(self.radial_stations),
            "axial_divisions": self.axial_divisions,
            "relaxed_ratio_tolerance": self.relaxed_ratio_tolerance,
        }


@dataclass(frozen=True, slots=True)
class Level0PhysicsRecord:
    """The level-0 models evaluated on one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the validated configuration the record was built from.
    inputs
        Declared model inputs.
    eigenvalue
        The conserver's Taylor eigenvalue.
    formation
        The formation disposition.
    field
        The relaxed-state field on the declared grid.
    """

    configuration_digest_sha256: str
    inputs: ModelInputs
    eigenvalue: TaylorEigenvalue
    formation: FormationDisposition
    field: tuple[FieldSample, ...]

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            Schema identity, non-claims, and every model record.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "non_claims": list(LEVEL0_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "inputs": self.inputs.to_record(),
            "eigenvalue": self.eigenvalue.to_record(),
            "formation": self.formation.to_record(),
            "field": [sample.to_record() for sample in self.field],
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
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration, inputs: ModelInputs
) -> Level0PhysicsRecord:
    """Evaluate every level-0 model on a validated configuration.

    Parameters
    ----------
    configuration
        Validated spheromak configuration.
    inputs
        Declared model inputs.

    Returns
    -------
    Level0PhysicsRecord
        The composed record.
    """
    eigenvalue = conserver_eigenvalue(configuration.geometry)
    formation = formation_disposition(
        configuration.source.gun_lambda_per_m(),
        eigenvalue.eigenvalue_per_m,
        inputs.relaxed_ratio_tolerance,
    )
    field = field_grid(
        eigenvalue,
        inputs.axis_field_t,
        inputs.radial_stations,
        inputs.axial_divisions,
    )
    return Level0PhysicsRecord(
        configuration_digest_sha256=configuration.digest_sha256(),
        inputs=inputs,
        eigenvalue=eigenvalue,
        formation=formation,
        field=field,
    )
