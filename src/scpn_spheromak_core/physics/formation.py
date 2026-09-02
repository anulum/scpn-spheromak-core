# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — formation disposition

"""The formation-source parameter against the conserver eigenvalue.

R. D. Wood et al., UCRL-JRNL-214703 (2005), OSTI 883741, use
``lambda_gun = mu0 I_gun / psi_gun`` as the figure of merit of coaxial
helicity injection and state the dispositions: "when we operate with
``lambda_gun > lambda_FC``, we expect to find 'hollow' current profiles";
"when operating with ``lambda_gun < lambda_FC``, we expect 'peaked'
current profiles"; "when ``lambda_gun ~= lambda_FC``, the current density
profile is kept close to the relaxed state, ``lambda = constant``". The
ratio ``lambda_gun / lambda_fc`` is reported with the disposition
``hollow`` above ``1 + tolerance``, ``peaked`` below ``1 - tolerance``
and ``relaxed`` within the declared tolerance; the tolerance is a
declared input, not a source value. The configuration model's advisory
(a source below the threshold) is the ``peaked`` side of this
disposition at zero tolerance. Nothing here describes a real machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from scpn_spheromak_core.errors import DeviceConfigurationError
from scpn_spheromak_core.parameters import require_finite, require_positive

DISPOSITION_HOLLOW: Final = "hollow"
DISPOSITION_PEAKED: Final = "peaked"
DISPOSITION_RELAXED: Final = "relaxed"


def require_ratio_tolerance(tolerance: float) -> float:
    """Return ``tolerance`` when it lies in ``[0, 1)``.

    Parameters
    ----------
    tolerance
        Half-width of the relaxed band around ``lambda_gun / lambda_fc = 1``.

    Returns
    -------
    float
        The validated tolerance.

    Raises
    ------
    DeviceConfigurationError
        If ``tolerance`` is non-finite, negative or at least one.
    """
    require_finite("relaxed_ratio_tolerance", tolerance)
    if not 0.0 <= tolerance < 1.0:
        raise DeviceConfigurationError(
            f"relaxed_ratio_tolerance: must be within [0, 1), got {tolerance!r}"
        )
    return tolerance


@dataclass(frozen=True, slots=True)
class FormationDisposition:
    """The source parameter against the eigenvalue.

    Parameters
    ----------
    gun_lambda_per_m
        ``lambda_gun``.
    eigenvalue_per_m
        ``lambda_fc``.
    ratio
        ``lambda_gun / lambda_fc``.
    relaxed_ratio_tolerance
        The declared band half-width.
    disposition
        ``hollow``, ``peaked`` or ``relaxed``.
    """

    gun_lambda_per_m: float
    eigenvalue_per_m: float
    ratio: float
    relaxed_ratio_tolerance: float
    disposition: str

    def to_record(self) -> dict[str, Any]:
        """Project the disposition to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "gun_lambda_per_m": self.gun_lambda_per_m,
            "eigenvalue_per_m": self.eigenvalue_per_m,
            "ratio": self.ratio,
            "relaxed_ratio_tolerance": self.relaxed_ratio_tolerance,
            "disposition": self.disposition,
        }


def formation_disposition(
    gun_lambda_per_m: float, eigenvalue_per_m: float, tolerance: float
) -> FormationDisposition:
    """Classify the source parameter against the eigenvalue.

    Parameters
    ----------
    gun_lambda_per_m
        ``lambda_gun``; strictly positive.
    eigenvalue_per_m
        ``lambda_fc``; strictly positive.
    tolerance
        Half-width of the relaxed band in ``[0, 1)``.

    Returns
    -------
    FormationDisposition
        The ratio and its disposition.

    Raises
    ------
    DeviceConfigurationError
        If an input is outside its domain.
    """
    require_positive("gun_lambda_per_m", gun_lambda_per_m)
    require_positive("eigenvalue_per_m", eigenvalue_per_m)
    band = require_ratio_tolerance(tolerance)
    ratio = gun_lambda_per_m / eigenvalue_per_m
    if ratio > 1.0 + band:
        disposition = DISPOSITION_HOLLOW
    elif ratio < 1.0 - band:
        disposition = DISPOSITION_PEAKED
    else:
        disposition = DISPOSITION_RELAXED
    return FormationDisposition(
        gun_lambda_per_m=gun_lambda_per_m,
        eigenvalue_per_m=eigenvalue_per_m,
        ratio=ratio,
        relaxed_ratio_tolerance=band,
        disposition=disposition,
    )
