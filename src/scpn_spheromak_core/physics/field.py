# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — relaxed-state field in the cylindrical flux conserver

"""The Chandrasekhar–Kendall field of the relaxed state in a cylinder.

With ``k_r = j_{1,1} / R``, ``k_z = pi / L`` and
``lambda = sqrt(k_r^2 + k_z^2)`` the lowest axisymmetric solution of
``curl B = lambda B`` in the right circular cylinder (the eigenvalue
problem of :mod:`scpn_spheromak_core.physics.eigenvalue`) is

- ``B_z(r, z) = B0 J0(k_r r) sin(k_z z)``,
- ``B_theta(r, z) = B0 (lambda / k_r) J1(k_r r) sin(k_z z)``,
- ``B_r(r, z) = -B0 (k_z / k_r) J1(k_r r) cos(k_z z)``,

which is divergence-free, satisfies ``curl B = lambda B`` component by
component, and meets the conducting wall (``B_r(R, z) = 0`` because
``J1(j_{1,1}) = 0``) and the end plates (``B_z(r, 0) = B_z(r, L) = 0``);
``B0`` is the axial field on the axis at the midplane. The field is
evaluated on a grid of declared stations: radial fractions ``r / R`` in
``[0, 1]`` (the Bessel argument ``k_r r = j_{1,1} (r / R)`` stays inside
the kernel domain) and axial stations ``z = k L / N`` for
``k = 0 .. N`` with ``N`` a multiple of four, whose phases
``(cos(pi k / N), sin(pi k / N))`` are the points ``k`` of the shared
library's unit circle with ``2 N`` segments (exact ``0`` and ``±1`` at
the plates and the midplane by the kernel's symmetry), so no platform
trigonometric function is called. The magnetic axis
``r = j'_{1,1} / k_r`` is not evaluated (the first zero of ``J1'`` is not
in the library). Nothing here describes a real machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import require_finite, require_positive
from scpn_spheromak_core.physics.eigenvalue import TaylorEigenvalue
from scpn_spheromak_core.physics.numerics import (
    BESSEL_J1_FIRST_ZERO,
    bessel_j0,
    bessel_j1,
    unit_circle,
)

#: Smallest admissible number of axial divisions (two unit-circle octants).
MIN_AXIAL_DIVISIONS: Final = 4
#: The axial divisions must be a multiple of this (the kernel's octant rule).
AXIAL_DIVISION_MULTIPLE: Final = 4


def require_radial_station(name: str, fraction: float) -> float:
    """Return ``fraction`` when it lies in ``[0, 1]``.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    fraction
        Normalised radius ``r / R``.

    Returns
    -------
    float
        The validated fraction.

    Raises
    ------
    DeviceConfigurationError
        If ``fraction`` is non-finite or outside ``[0, 1]``.
    """
    require_finite(name, fraction)
    if not 0.0 <= fraction <= 1.0:
        raise DeviceConfigurationError(
            f"{name}: a radial station is r / R within [0, 1], got {fraction!r}"
        )
    return fraction


def require_axial_divisions(divisions: int) -> int:
    """Return ``divisions`` when it is a positive multiple of four.

    Parameters
    ----------
    divisions
        Number ``N`` of axial intervals between the end plates.

    Returns
    -------
    int
        The validated count.

    Raises
    ------
    DeviceConfigurationError
        If ``divisions`` is below four or not a multiple of four.
    """
    if isinstance(divisions, bool) or divisions < MIN_AXIAL_DIVISIONS:
        raise DeviceConfigurationError(
            f"axial_divisions: must be at least {MIN_AXIAL_DIVISIONS}, "
            f"got {divisions!r}"
        )
    if divisions % AXIAL_DIVISION_MULTIPLE != 0:
        raise DeviceConfigurationError(
            f"axial_divisions: must be a multiple of {AXIAL_DIVISION_MULTIPLE}, "
            f"got {divisions!r}"
        )
    return divisions


def axial_phases(divisions: int) -> tuple[tuple[float, float], ...]:
    """Return ``(cos, sin)`` of ``pi k / N`` for ``k = 0 .. N``.

    Parameters
    ----------
    divisions
        ``N``; at least four and a multiple of four.

    Returns
    -------
    tuple of (float, float)
        The first ``N + 1`` points of the library's unit circle with
        ``2 N`` segments.

    Raises
    ------
    DeviceConfigurationError
        If ``divisions`` is invalid.
    """
    count = require_axial_divisions(divisions)
    return unit_circle(2 * count)[: count + 1]


@dataclass(frozen=True, slots=True)
class FieldSample:
    """The relaxed-state field at one grid station.

    Parameters
    ----------
    radial_fraction
        ``r / R``.
    axial_fraction
        ``z / L``.
    radius_m
        ``r``.
    height_m
        ``z``.
    radial_field_t
        ``B_r``.
    azimuthal_field_t
        ``B_theta``.
    axial_field_t
        ``B_z``.
    """

    radial_fraction: float
    axial_fraction: float
    radius_m: float
    height_m: float
    radial_field_t: float
    azimuthal_field_t: float
    axial_field_t: float

    def to_record(self) -> dict[str, Any]:
        """Project the sample to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "radial_fraction": self.radial_fraction,
            "axial_fraction": self.axial_fraction,
            "radius_m": self.radius_m,
            "height_m": self.height_m,
            "radial_field_t": self.radial_field_t,
            "azimuthal_field_t": self.azimuthal_field_t,
            "axial_field_t": self.axial_field_t,
        }


def field_sample(
    radial_fraction: float,
    axial_fraction: float,
    cosine: float,
    sine: float,
    eigenvalue: TaylorEigenvalue,
    axis_field_t: float,
) -> FieldSample:
    """Evaluate the field at one station.

    Parameters
    ----------
    radial_fraction
        ``r / R`` in ``[0, 1]``.
    axial_fraction
        ``z / L`` (reported; the phase is passed explicitly).
    cosine
        ``cos(k_z z)`` from the library's unit circle.
    sine
        ``sin(k_z z)`` from the library's unit circle.
    eigenvalue
        The conserver's eigenvalue and wavenumbers.
    axis_field_t
        ``B0``; strictly positive.

    Returns
    -------
    FieldSample
        The three components at the station.

    Raises
    ------
    DeviceConfigurationError
        If the radial station is outside ``[0, 1]`` or ``B0`` is not
        strictly positive.
    """
    require_radial_station("radial_fraction", radial_fraction)
    require_positive("axis_field_t", axis_field_t)
    argument = BESSEL_J1_FIRST_ZERO * radial_fraction
    j0 = bessel_j0(argument)
    j1 = bessel_j1(argument)
    radial_ratio = eigenvalue.eigenvalue_per_m / eigenvalue.radial_wavenumber_per_m
    axial_ratio = eigenvalue.axial_wavenumber_per_m / eigenvalue.radial_wavenumber_per_m
    return FieldSample(
        radial_fraction=radial_fraction,
        axial_fraction=axial_fraction,
        radius_m=radial_fraction * eigenvalue.radius_m,
        height_m=axial_fraction * eigenvalue.length_m,
        radial_field_t=-(axis_field_t * axial_ratio * j1 * cosine),
        azimuthal_field_t=axis_field_t * radial_ratio * j1 * sine,
        axial_field_t=axis_field_t * j0 * sine,
    )


def field_grid(
    eigenvalue: TaylorEigenvalue,
    axis_field_t: float,
    radial_stations: tuple[float, ...],
    axial_divisions: int,
) -> tuple[FieldSample, ...]:
    """Evaluate the field on the declared grid.

    Parameters
    ----------
    eigenvalue
        The conserver's eigenvalue and wavenumbers.
    axis_field_t
        ``B0``.
    radial_stations
        Normalised radii ``r / R``.
    axial_divisions
        ``N``; the axial stations are ``k / N`` for ``k = 0 .. N``.

    Returns
    -------
    tuple of FieldSample
        Radial stations outermost, axial stations innermost.
    """
    phases = axial_phases(axial_divisions)
    return tuple(
        field_sample(
            fraction,
            index / axial_divisions,
            cosine,
            sine,
            eigenvalue,
            axis_field_t,
        )
        for fraction in radial_stations
        for index, (cosine, sine) in enumerate(phases)
    )
