# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — Taylor-state eigenvalue of the flux conserver

"""The Taylor-state eigenvalue of a cylindrical flux conserver.

The relaxed state of a spheromak inside a conducting flux conserver is
the lowest homogeneous solution of ``curl B = lambda_fc B`` in that
conserver (E. B. Hooper et al., "Reactor opportunities for the
spheromak", 2003, OSTI 15005037: "the eigenvalue is defined as the
homogeneous solution to ``curl B = lambda_fc B`` in the flux
conserver"); the mean ``lambda = mu0 J / B`` of the plasma matches it
(R. D. Wood et al., UCRL-JRNL-214703 (2005), OSTI 883741: "the mean
lambda of the spheromak matches the Taylor state geometric eigenvalue of
the flux conserver, ``lambda_FC = 9.9 m^-1``" for the SSPX conserver of
"1 m diameter by 0.5 m high"). For a right circular cylinder of radius
``R`` and length ``L`` with a conducting wall (``B_r(R) = 0``) and
conducting end plates (``B_z(0) = B_z(L) = 0``) the separated solution
has the radial wavenumber ``k_r = j_{1,1} / R`` and the axial
wavenumber ``k_z = pi / L``, and the eigenvalue is
``lambda_fc = sqrt(k_r^2 + k_z^2)`` (the separation form of the
Chandrasekhar–Kendall field; the first zero ``j_{1,1}`` from the
shared kernel library, DLMF 10.21 and OEIS A115369). At a fixed shape
``L / R`` the eigenvalue is inversely proportional to the radius
(PPPL-2257 (1985), OSTI 5141825: "for a given plasma shape, the
eigenvalue is inversely proportional to the midplane separatrix
radius"). The configuration model's ``taylor_eigenvalue_per_m`` is the
same evaluation; this module restates it with its wavenumbers.
Nothing here describes a real machine: the SSPX number is the anchor of
a printed eigenvalue only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from scpn_spheromak_core.parameters import FluxConserverGeometry, require_positive
from scpn_spheromak_core.physics.numerics import BESSEL_J1_FIRST_ZERO


@dataclass(frozen=True, slots=True)
class TaylorEigenvalue:
    """The cylindrical Taylor eigenvalue and its wavenumbers.

    Parameters
    ----------
    radius_m
        Flux-conserver radius ``R``.
    length_m
        Flux-conserver length ``L``.
    radial_wavenumber_per_m
        ``k_r = j_{1,1} / R``.
    axial_wavenumber_per_m
        ``k_z = pi / L``.
    eigenvalue_per_m
        ``lambda_fc = sqrt(k_r^2 + k_z^2)``.
    """

    radius_m: float
    length_m: float
    radial_wavenumber_per_m: float
    axial_wavenumber_per_m: float
    eigenvalue_per_m: float

    def to_record(self) -> dict[str, Any]:
        """Project the eigenvalue to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "radius_m": self.radius_m,
            "length_m": self.length_m,
            "radial_wavenumber_per_m": self.radial_wavenumber_per_m,
            "axial_wavenumber_per_m": self.axial_wavenumber_per_m,
            "eigenvalue_per_m": self.eigenvalue_per_m,
        }


def taylor_eigenvalue(radius_m: float, length_m: float) -> TaylorEigenvalue:
    """Evaluate the cylindrical Taylor eigenvalue.

    Parameters
    ----------
    radius_m
        Flux-conserver radius ``R``; strictly positive.
    length_m
        Flux-conserver length ``L``; strictly positive.

    Returns
    -------
    TaylorEigenvalue
        The wavenumbers and the eigenvalue.

    Raises
    ------
    DeviceConfigurationError
        If either extent is not strictly positive.
    """
    require_positive("radius_m", radius_m)
    require_positive("length_m", length_m)
    radial = BESSEL_J1_FIRST_ZERO / radius_m
    axial = math.pi / length_m
    return TaylorEigenvalue(
        radius_m=radius_m,
        length_m=length_m,
        radial_wavenumber_per_m=radial,
        axial_wavenumber_per_m=axial,
        eigenvalue_per_m=math.sqrt(radial * radial + axial * axial),
    )


def conserver_eigenvalue(geometry: FluxConserverGeometry) -> TaylorEigenvalue:
    """Evaluate the eigenvalue of a validated flux conserver.

    Parameters
    ----------
    geometry
        Validated flux-conserver geometry.

    Returns
    -------
    TaylorEigenvalue
        The eigenvalue; ``eigenvalue_per_m`` equals the configuration
        model's ``taylor_eigenvalue_per_m()`` bit for bit.
    """
    return taylor_eigenvalue(geometry.radius_m, geometry.length_m)
