# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — level-0 device physics

"""Level-0 device physics of the spheromak family.

The cylindrical Taylor eigenvalue of the flux conserver (the lowest
homogeneous solution of ``curl B = lambda B``; Hooper et al. 2003, Wood
et al. 2005, PPPL-2257), the Chandrasekhar–Kendall field of that relaxed
state on a declared grid, and the formation disposition of the coaxial
source against the eigenvalue (Wood et al. 2005), evaluated on the
validated device configuration. Every function is a closed-form
evaluation on the shared Bessel and unit-circle kernels; no equation is
solved and no value describes a real machine. Design records: ADR 0005,
ADR 0006.
"""

from __future__ import annotations

from scpn_spheromak_core.physics.eigenvalue import (
    TaylorEigenvalue,
    conserver_eigenvalue,
    taylor_eigenvalue,
)
from scpn_spheromak_core.physics.field import (
    AXIAL_DIVISION_MULTIPLE,
    MIN_AXIAL_DIVISIONS,
    FieldSample,
    axial_phases,
    field_grid,
    field_sample,
    require_axial_divisions,
    require_radial_station,
)
from scpn_spheromak_core.physics.formation import (
    DISPOSITION_HOLLOW,
    DISPOSITION_PEAKED,
    DISPOSITION_RELAXED,
    FormationDisposition,
    formation_disposition,
    require_ratio_tolerance,
)
from scpn_spheromak_core.physics.level0 import (
    LEVEL0_AXIAL_DIVISIONS,
    LEVEL0_NON_CLAIMS,
    LEVEL0_RADIAL_STATIONS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0PhysicsRecord,
    ModelInputs,
    level0_physics,
)
from scpn_spheromak_core.physics.numerics import (
    BESSEL_DOMAIN,
    BESSEL_J1_FIRST_ZERO,
    bessel_j0,
    bessel_j1,
    unit_circle,
)

__all__ = [
    "AXIAL_DIVISION_MULTIPLE",
    "BESSEL_DOMAIN",
    "BESSEL_J1_FIRST_ZERO",
    "DISPOSITION_HOLLOW",
    "DISPOSITION_PEAKED",
    "DISPOSITION_RELAXED",
    "LEVEL0_AXIAL_DIVISIONS",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_RADIAL_STATIONS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MIN_AXIAL_DIVISIONS",
    "FieldSample",
    "FormationDisposition",
    "Level0PhysicsRecord",
    "ModelInputs",
    "TaylorEigenvalue",
    "axial_phases",
    "bessel_j0",
    "bessel_j1",
    "conserver_eigenvalue",
    "field_grid",
    "field_sample",
    "formation_disposition",
    "level0_physics",
    "require_axial_divisions",
    "require_radial_station",
    "require_ratio_tolerance",
    "taylor_eigenvalue",
    "unit_circle",
]
