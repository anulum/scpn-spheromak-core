# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — numerics wrapper tests

"""The library kernels are the only special-function path; refusals re-raised."""

from __future__ import annotations

import pytest
from scpn_reactor_kernels import geometry as library_geometry
from scpn_reactor_kernels import numerics as library

from scpn_spheromak_core.errors import DeviceConfigurationError, NumericsError
from scpn_spheromak_core.parameters import BESSEL_J1_FIRST_ZERO as MODEL_ZERO
from scpn_spheromak_core.physics import (
    BESSEL_DOMAIN,
    BESSEL_J1_FIRST_ZERO,
    bessel_j0,
    bessel_j1,
    unit_circle,
)


def test_wrappers_return_the_library_values_bit_for_bit() -> None:
    """Every wrapper is the library kernel; the zero is the library's constant."""
    assert bessel_j0(2.0) == library.bessel_j0(2.0)
    assert bessel_j1(2.0) == library.bessel_j1(2.0)
    assert unit_circle(8) == library_geometry.unit_circle(8)
    assert BESSEL_J1_FIRST_ZERO == library.BESSEL_J1_FIRST_ZERO == MODEL_ZERO
    assert BESSEL_DOMAIN == library.BESSEL_DOMAIN
    assert abs(bessel_j1(BESSEL_J1_FIRST_ZERO)) <= 1.0e-14
    assert unit_circle(8)[2] == (0.0, 1.0)
    assert unit_circle(8)[4] == (-1.0, 0.0)


@pytest.mark.parametrize(
    ("call", "fragment"),
    [
        (lambda: bessel_j0(9.0), "x"),
        (lambda: bessel_j1(float("nan")), "finite"),
        (lambda: unit_circle(6), "segments"),
        (lambda: unit_circle(12), "multiple"),
    ],
)
def test_refusals_are_re_raised_under_the_device_error(
    call: object, fragment: str
) -> None:
    """A library refusal becomes a NumericsError that is a configuration error."""
    assert callable(call)
    with pytest.raises(NumericsError, match=fragment) as info:
        call()
    assert isinstance(info.value, DeviceConfigurationError)
    assert info.value.__cause__ is not None
