# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — device capability package

"""Device capability models of the SCPN spheromak device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics``, ``level0_device_physics``,
``device_3d_model`` and ``device_cad_model`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, the cylindrical
Taylor eigenvalue, the relaxed-state field and the formation disposition
evaluated on the validated configuration through the pinned shared Bessel
and unit-circle kernels, a validated device geometry with a deterministic
tier-G1 3D model and the tier-G2 B-rep CAD model of the same design with a
normalised deterministic STEP export, canonical serialisation with SHA-256
digests, and data-only pins to the SPO registries. No claim about any real
machine or diagnostic is made anywhere in this package.
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
    DeviceGeometryError,
    DiagnosticPlanError,
    NumericsError,
)
from scpn_spheromak_core.geometry import (
    BODY_NAMES,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    GEOMETRY_FIELDS,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    DeviceGeometry,
    DeviceModel3D,
    DeviceModelCAD,
    build_device_cad,
    build_device_model,
    check_layout_invariants,
    geometry_from_bytes,
    geometry_from_record,
    glb_bytes,
    glb_extras,
    stl_bytes,
    write_glb,
    write_step,
    write_stl,
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
    "BODY_NAMES",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CATALOGUE_BINDING",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "GEOMETRY_FIELDS",
    "LEVEL0_AXIAL_DIVISIONS",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_RADIAL_STATIONS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
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
    "DeviceGeometry",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
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
    "build_device_cad",
    "build_device_model",
    "check_layout_invariants",
    "configuration_from_bytes",
    "configuration_from_record",
    "conserver_eigenvalue",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "field_grid",
    "formation_disposition",
    "geometry_from_bytes",
    "geometry_from_record",
    "glb_bytes",
    "glb_extras",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "stl_bytes",
    "taylor_eigenvalue",
    "verify_envelope",
    "write_glb",
    "write_step",
    "write_stl",
]
