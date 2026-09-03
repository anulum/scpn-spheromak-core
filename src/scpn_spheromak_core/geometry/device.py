# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device geometry model

"""Validated device geometry of a coaxial-gun spheromak assembly.

The geometry complements the
:class:`~scpn_spheromak_core.configuration.DeviceConfiguration` (which
carries the flux-conserver bore and length and the formation source) with
the device-owned mechanical envelope: the conserver wall, the coaxial gun
electrodes below the conserver, and the end wall closing the conserver
opposite the gun. The layout is the arrangement of the gun-driven
spheromak described by Wood et al., "Improved operation of the SSPX
spheromak", UCRL-JRNL-214703 (2005): a coaxial gun whose outer electrode
is contiguous with the flux-conserver wall, below a cylindrical conserver
closed at the far end. Parameter sets are declared by the caller: the
repository's own fixtures are synthetic, and one anchor fixture carries
the conserver dimensions that source prints so the tier can be checked
against a published arrangement. Reproducing a printed dimension is an
anchor, never a claim about that machine.

The conserver bore radius and length are not repeated here: they are the
validated configuration's ``geometry.radius_m`` and ``geometry.length_m``,
checked against this geometry when the model is built. Validation is
fail-closed, serialisation is canonical, and the SHA-256 digest
identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_spheromak_core.errors import DeviceGeometryError
from scpn_spheromak_core.parameters import require_positive

GEOMETRY_FIELDS: Final = (
    "conserver_wall_thickness_m",
    "gun_inner_electrode_radius_m",
    "gun_outer_electrode_inner_radius_m",
    "gun_outer_electrode_wall_thickness_m",
    "gun_length_m",
    "end_wall_thickness_m",
)


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule with the geometry error type.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DeviceGeometry:
    """Validated gun-driven spheromak geometry (SI units in the field names).

    Parameters
    ----------
    conserver_wall_thickness_m
        Radial wall thickness of the flux conserver; strictly positive.
    gun_inner_electrode_radius_m
        Radius of the solid gun inner electrode; strictly positive and
        smaller than the gun outer electrode bore.
    gun_outer_electrode_inner_radius_m
        Bore radius of the gun outer electrode; strictly positive.
    gun_outer_electrode_wall_thickness_m
        Radial wall thickness of the gun outer electrode; strictly
        positive.
    gun_length_m
        Axial length of the coaxial gun below the conserver; strictly
        positive.
    end_wall_thickness_m
        Axial thickness of the end wall closing the conserver opposite
        the gun; strictly positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive, or if the
        inner electrode does not fit inside the gun outer electrode bore.
    """

    conserver_wall_thickness_m: float
    gun_inner_electrode_radius_m: float
    gun_outer_electrode_inner_radius_m: float
    gun_outer_electrode_wall_thickness_m: float
    gun_length_m: float
    end_wall_thickness_m: float

    def __post_init__(self) -> None:
        """Validate every value and the gun radial containment invariant.

        Raises
        ------
        DeviceGeometryError
            If any invariant fails.
        """
        for name in GEOMETRY_FIELDS:
            _positive(name, getattr(self, name))
        if self.gun_inner_electrode_radius_m >= self.gun_outer_electrode_inner_radius_m:
            raise DeviceGeometryError(
                "gun_inner_electrode_radius_m: must be smaller than "
                "gun_outer_electrode_inner_radius_m, got "
                f"{self.gun_inner_electrode_radius_m!r} >= "
                f"{self.gun_outer_electrode_inner_radius_m!r}"
            )

    @property
    def gun_outer_electrode_outer_radius_m(self) -> float:
        """Outer radius of the gun outer electrode (bore plus wall)."""
        return (
            self.gun_outer_electrode_inner_radius_m
            + self.gun_outer_electrode_wall_thickness_m
        )

    def to_record(self) -> dict[str, float]:
        """Project the geometry to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in GEOMETRY_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the geometry canonically.

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
        """Identify the exact geometry.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Raises
    ------
    DeviceGeometryError
        If the field is missing or not a real number (booleans rejected).
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DeviceGeometryError(f"{field}: must be a number, got {value!r}")
    return float(value)


def geometry_from_record(record: Any) -> DeviceGeometry:
    """Build a validated geometry from a decoded record.

    Parameters
    ----------
    record
        Decoded JSON object in the shape produced by
        :meth:`DeviceGeometry.to_record`.

    Returns
    -------
    DeviceGeometry
        The fully validated geometry.

    Raises
    ------
    DeviceGeometryError
        If the record shape or any value violates the model; unknown
        fields are refused.
    """
    if not isinstance(record, dict):
        raise DeviceGeometryError("record: must be an object")
    unknown = sorted(set(record) - set(GEOMETRY_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"record: unknown fields {unknown!r}")
    return DeviceGeometry(**{name: _number(record, name) for name in GEOMETRY_FIELDS})


def geometry_from_bytes(data: bytes) -> DeviceGeometry:
    """Build a validated geometry from canonical JSON bytes.

    Parameters
    ----------
    data
        UTF-8 JSON document; NaN and infinity literals are rejected.

    Returns
    -------
    DeviceGeometry
        The fully validated geometry.

    Raises
    ------
    DeviceGeometryError
        If the document is not valid strict JSON or violates the model.
    """

    def _reject_constant(literal: str) -> float:
        raise DeviceGeometryError(
            f"record: non-finite JSON literal {literal!r} is rejected"
        )

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeviceGeometryError(f"record: invalid JSON document: {exc}") from exc
    return geometry_from_record(record)
