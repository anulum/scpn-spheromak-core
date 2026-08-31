# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — spheromak parameter model

"""Validated parameter objects of a spheromak configuration.

The derived quantities implement two standard results and nothing more:
the Taylor-state eigenvalue of a cylindrical flux conserver
``lambda_fc = sqrt((x11 / R)^2 + (pi / L)^2)`` with ``x11 = 3.832``
(first zero of the Bessel function J1), and the formation-source
parameter ``lambda_gun = mu0 I_gun / Phi_bias`` (P. M. Bellan,
Spheromaks, Imperial College Press, 2000, chs. 3-4). Both are rough
consistency instruments with documented applicability bounds; no claim
about any real machine follows from them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_spheromak_core.errors import DeviceConfigurationError

BESSEL_J1_FIRST_ZERO: Final = 3.832
MU0: Final = 4.0e-7 * math.pi


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

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
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

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
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class FluxConserverGeometry:
    """Cylindrical flux-conserver geometry parameters.

    Parameters
    ----------
    radius_m
        Flux-conserver radius ``R`` in metres; strictly positive.
    length_m
        Flux-conserver length ``L`` in metres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    radius_m: float
    length_m: float

    def __post_init__(self) -> None:
        """Validate the flux-conserver invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("radius_m", self.radius_m)
        require_positive("length_m", self.length_m)

    def taylor_eigenvalue_per_m(self) -> float:
        """Taylor-state eigenvalue of the cylindrical flux conserver.

        Returns
        -------
        float
            ``lambda_fc = sqrt((3.832 / R)^2 + (pi / L)^2)`` in inverse
            metres — the force-free eigenvalue of the minimum-energy
            state in a cylindrical conserver (Bellan 2000, ch. 3).
        """
        return math.sqrt(
            (BESSEL_J1_FIRST_ZERO / self.radius_m) ** 2 + (math.pi / self.length_m) ** 2
        )


@dataclass(frozen=True, slots=True)
class FormationSource:
    """Coaxial-gun formation-source parameters.

    Parameters
    ----------
    gun_current_ma
        Peak gun current ``I_gun`` in mega-amperes; strictly positive.
    bias_flux_mwb
        Bias (stuffing) poloidal flux ``Phi_bias`` in milliwebers;
        strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    gun_current_ma: float
    bias_flux_mwb: float

    def __post_init__(self) -> None:
        """Validate the formation-source invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("gun_current_ma", self.gun_current_ma)
        require_positive("bias_flux_mwb", self.bias_flux_mwb)

    def gun_lambda_per_m(self) -> float:
        """Formation-source parameter of the coaxial gun.

        Returns
        -------
        float
            ``lambda_gun = mu0 I_gun / Phi_bias`` in inverse metres,
            with the current in amperes and the flux in webers
            (Bellan 2000, ch. 4).
        """
        return MU0 * (self.gun_current_ma * 1.0e6) / (self.bias_flux_mwb * 1.0e-3)
