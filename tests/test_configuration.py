# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device configuration container tests

"""Every branch of the device configuration container and its parsers.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from scpn_spheromak_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import (
    FluxConserverGeometry,
    FormationSource,
)

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)


def synthetic_configuration(
    identifier: str = "spheromak",
    bias_flux_mwb: float = 15.0,
    *,
    external_toroidal_field_coils: bool = False,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration with optional overrides."""
    return DeviceConfiguration(
        identifier=identifier,
        geometry=FluxConserverGeometry(radius_m=0.5, length_m=1.0),
        source=FormationSource(gun_current_ma=0.1, bias_flux_mwb=bias_flux_mwb),
        external_toroidal_field_coils=external_toroidal_field_coils,
        registry=REGISTRY,
    )


def test_registry_binding_rejects_bad_pins() -> None:
    """Malformed registry pins are rejected."""
    with pytest.raises(DeviceConfigurationError, match=r"registry\.version"):
        RegistryBinding(version="", digest_sha256="0" * 64)
    with pytest.raises(DeviceConfigurationError, match=r"registry\.digest_sha256"):
        RegistryBinding(version="1.0.0", digest_sha256="ZZ")


def test_owned_identifier_constructs() -> None:
    """The owned identifier constructs with a consistent source."""
    assert synthetic_configuration().identifier == "spheromak"


def test_unowned_identifier_is_rejected() -> None:
    """Identifiers outside this repository's ownership are rejected."""
    with pytest.raises(DeviceConfigurationError, match="not owned"):
        synthetic_configuration("field_reversed_configuration")


def test_external_toroidal_coils_are_rejected() -> None:
    """Declaring external toroidal-field coils contradicts the class."""
    with pytest.raises(DeviceConfigurationError, match="self-generated"):
        synthetic_configuration(external_toroidal_field_coils=True)


def test_consistency_report_clean_and_finding() -> None:
    """The report is empty above threshold and precise below it."""
    assert synthetic_configuration().consistency_report() == ()
    below = synthetic_configuration(bias_flux_mwb=20.0)
    findings = below.consistency_report()
    assert len(findings) == 1
    assert findings[0].field == "source.gun_current_ma"
    assert "formation is not" in findings[0].message


def test_canonical_round_trip_and_digest() -> None:
    """Canonical bytes round-trip losslessly and digest deterministically."""
    configuration = synthetic_configuration()
    data = configuration.canonical_bytes()
    assert data.endswith(b"\n")
    restored = configuration_from_bytes(data)
    assert restored == configuration
    expected = hashlib.sha256(data).hexdigest()
    assert configuration.digest_sha256() == expected


def test_from_record_round_trip() -> None:
    """The owned configuration round-trips through records."""
    configuration = synthetic_configuration()
    assert configuration_from_record(configuration.to_record()) == configuration


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (lambda _: "not-a-dict", "record: must be an object"),
        (lambda r: {**r, "extra": 1}, "unknown fields"),
        (lambda r: {**r, "geometry": None}, "geometry: must be an object"),
        (lambda r: {**r, "source": []}, "source: must be an object"),
        (lambda r: {**r, "registry": 7}, "registry: must be an object"),
        (lambda r: {**r, "identifier": 3}, "identifier: must be a string"),
        (
            lambda r: {**r, "external_toroidal_field_coils": "no"},
            "external_toroidal_field_coils: must be a boolean",
        ),
    ],
)
def test_from_record_shape_violations(mutate: Any, fragment: str) -> None:
    """Each record-shape violation is rejected with a precise message."""
    record = synthetic_configuration().to_record()
    with pytest.raises(DeviceConfigurationError, match=fragment):
        configuration_from_record(mutate(record))


def test_from_record_field_type_violations() -> None:
    """Nested field-type violations name the offending field."""
    record = synthetic_configuration().to_record()
    record["geometry"]["radius_m"] = "big"
    with pytest.raises(DeviceConfigurationError, match="radius_m: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["source"]["gun_current_ma"] = True
    with pytest.raises(DeviceConfigurationError, match="gun_current_ma: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["registry"]["version"] = None
    with pytest.raises(DeviceConfigurationError, match="version: must be a string"):
        configuration_from_record(record)


def test_from_bytes_rejects_invalid_documents() -> None:
    """Invalid UTF-8, invalid JSON, and non-finite literals are rejected."""
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"\xff\xfe")
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"{not json")
    record = synthetic_configuration().to_record()
    text = json.dumps(record).replace("0.5", "NaN", 1)
    with pytest.raises(DeviceConfigurationError, match="non-finite JSON literal"):
        configuration_from_bytes(text.encode("utf-8"))


def test_integer_accepted_where_number_expected() -> None:
    """Integral JSON numbers are accepted for real-valued fields."""
    record = synthetic_configuration().to_record()
    record["geometry"]["length_m"] = 1
    restored = configuration_from_record(record)
    assert restored.geometry.length_m == 1.0
