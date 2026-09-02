# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device capability package

"""Device capability models of the SCPN spheromak device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics`` and ``level0_device_physics`` capabilities
at ``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, the cylindrical
Taylor eigenvalue, the relaxed-state field and the formation disposition
evaluated on the validated configuration through the pinned shared Bessel
and unit-circle kernels, canonical serialisation with SHA-256 digests, and
data-only pins to the SPO registries. No claim about any real machine or
diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_spheromak_core.configuration import (
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_spheromak_core.errors import (
    DeviceConfigurationError,
    DiagnosticPlanError,
    NumericsError,
)
from scpn_spheromak_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_spheromak_core.parameters import (
    BESSEL_J1_FIRST_ZERO,
    MU0,
    FluxConserverGeometry,
    FormationSource,
)
from scpn_spheromak_core.physics import (
    LEVEL0_AXIAL_DIVISIONS,
    LEVEL0_NON_CLAIMS,
    LEVEL0_RADIAL_STATIONS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    FieldSample,
    FormationDisposition,
    Level0PhysicsRecord,
    ModelInputs,
    TaylorEigenvalue,
    conserver_eigenvalue,
    field_grid,
    formation_disposition,
    level0_physics,
    taylor_eigenvalue,
)
from scpn_spheromak_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BESSEL_J1_FIRST_ZERO",
    "CATALOGUE_BINDING",
    "LEVEL0_AXIAL_DIVISIONS",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_RADIAL_STATIONS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MU0",
    "OWNED_CONFIGURATIONS",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FieldSample",
    "FluxConserverGeometry",
    "FormationDisposition",
    "FormationSource",
    "FrameKind",
    "Level0PhysicsRecord",
    "ModelInputs",
    "NumericsError",
    "ObservabilityBinding",
    "ObservabilityClass",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "TaylorEigenvalue",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "conserver_eigenvalue",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "field_grid",
    "formation_disposition",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "taylor_eigenvalue",
    "verify_envelope",
]
