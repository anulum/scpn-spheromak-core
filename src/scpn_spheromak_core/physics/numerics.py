# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — shared numerics kernels

"""The Bessel and unit-circle kernels of the shared library.

The level-0 models use only ``+ - * /`` and ``sqrt`` plus two
deterministic kernels of the pinned shared kernel library
(``scpn_reactor_kernels``): the Bessel functions ``J0`` and ``J1`` with
the first zero ``j_{1,1}`` (kernel ``numerics_bessel``: the NIST DLMF
10.2.2 series on ``|x| <= 8``; OEIS A115369) and the equally spaced
unit-circle points (kernel ``geometry_unit_circle``: vendored sine and
cosine polynomials with exact octant symmetry), never a platform special
or trigonometric function, so the Python floor and the native crate
(which depends on the same library's Rust crate) agree bit for bit. A
domain refusal of the library is re-raised as
:class:`~scpn_spheromak_core.errors.NumericsError` with the library's
message.
"""

from __future__ import annotations

from scpn_reactor_kernels.errors import KernelInputError
from scpn_reactor_kernels.geometry import unit_circle as _unit_circle
from scpn_reactor_kernels.numerics import BESSEL_DOMAIN, BESSEL_J1_FIRST_ZERO
from scpn_reactor_kernels.numerics import bessel_j0 as _bessel_j0
from scpn_reactor_kernels.numerics import bessel_j1 as _bessel_j1

from scpn_spheromak_core.errors import NumericsError

__all__ = [
    "BESSEL_DOMAIN",
    "BESSEL_J1_FIRST_ZERO",
    "bessel_j0",
    "bessel_j1",
    "unit_circle",
]


def bessel_j0(x: float) -> float:
    """Return ``J0(x)`` by the library kernel.

    Parameters
    ----------
    x
        Argument with ``|x| <= 8``.

    Returns
    -------
    float
        The Bessel function of the first kind, order zero.

    Raises
    ------
    NumericsError
        If the library refuses the argument.
    """
    try:
        return _bessel_j0(x)
    except KernelInputError as exc:
        raise NumericsError(str(exc)) from exc


def bessel_j1(x: float) -> float:
    """Return ``J1(x)`` by the library kernel.

    Parameters
    ----------
    x
        Argument with ``|x| <= 8``.

    Returns
    -------
    float
        The Bessel function of the first kind, order one.

    Raises
    ------
    NumericsError
        If the library refuses the argument.
    """
    try:
        return _bessel_j1(x)
    except KernelInputError as exc:
        raise NumericsError(str(exc)) from exc


def unit_circle(segments: int) -> tuple[tuple[float, float], ...]:
    """Return the library's equally spaced unit-circle points.

    Parameters
    ----------
    segments
        Number of points; at least 8 and a multiple of 8.

    Returns
    -------
    tuple of (float, float)
        ``(cos, sin)`` of ``2 pi k / segments`` for ``k = 0 .. segments - 1``.

    Raises
    ------
    NumericsError
        If the library refuses the segment count.
    """
    try:
        return _unit_circle(segments)
    except KernelInputError as exc:
        raise NumericsError(str(exc)) from exc
