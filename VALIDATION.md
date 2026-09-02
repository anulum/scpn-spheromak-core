<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Spheromak Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests benchmarks` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary, the optional shared-kernel-library pin |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Native crate | `make rust` | format, lint and unit tests of the optional native kernels (fetches the pinned kernel crate) |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage; native crate gates, bit-exact parity and a benchmark smoke |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-SPHEROMAK-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`FluxConserverGeometry`,
  `FormationSource`, `DeviceConfiguration`) rejecting non-finite values,
  non-positive extents, and the hard class invariant that external
  toroidal-field coils are absent (the spheromak toroidal field is
  self-generated; Bellan, Spheromaks, 2000) — every rejection branch is
  tested.
- Advisory consistency findings with documented bounds, reported and
  never clamped: the formation-source parameter
  `lambda_gun = mu0 I_gun / Phi_bias` is compared with the cylindrical
  flux-conserver Taylor eigenvalue
  `lambda_fc = sqrt((j11/R)^2 + (pi/L)^2)` with `j11` the shared kernel
  library's correctly rounded first zero of `J1` (the earlier literal
  `3.832` was its rounding; ADR 0002 addendum); a source below the
  threshold is flagged (Bellan 2000, chs. 3-4).
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not equilibrium, relaxation,
  or stability results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design records:
`docs/adr/0005-level0-device-physics.md` and
`docs/adr/0006-shared-numerics-kernels.md`). Sources (all freely
available): R. D. Wood et al., "Improved operation of the SSPX
spheromak", UCRL-JRNL-214703 (2005), OSTI 883741; E. B. Hooper et al.,
"Reactor opportunities for the spheromak" (2003), OSTI 15005037;
PPPL-2257, "Verification of the Taylor state in the S-1 spheromak" (1985),
OSTI 5141825; the Bessel functions, their zeros and the unit circle
through the pinned shared kernel library (NIST DLMF 10.2.2, 10.21; OEIS
A115369).

What is exercised, all under the 100 % statement-and-branch coverage gate
(`src/scpn_spheromak_core/physics/`):

- **Numerics substrate** (`numerics.py`): ``J0``, ``J1``, the zero
  ``j_{1,1}`` and the unit circle are the pinned shared kernel library's
  (`scpn-reactor-kernels`, kernels `numerics_bessel` and
  `geometry_unit_circle`; commit and inventory digest in
  `reactor-domain.json`, `kernel_library`); tests prove each wrapper
  returns the library value bit for bit, that the zero is the same
  constant the configuration model uses, and that a library refusal
  (Bessel argument outside ``|x| <= 8`` or non-finite; a segment count
  below eight or not a multiple of eight) is re-raised as `NumericsError`
  (a configuration error). The manifest block is validated field by field
  and a contract test proves the manifest, the `pyproject.toml`
  dependency, the installed library version, `rust/Cargo.toml`,
  `rust/Cargo.lock` and the CI install steps name one commit.
- **Taylor eigenvalue** (`eigenvalue.py`; Hooper 2003 definition, Wood
  2005 value, PPPL-2257 scaling): the SSPX conserver ("1 m diameter by
  0.5 m high") gives ``lambda_fc = 9.91 m^-1`` against the printed
  ``9.9 m^-1`` within the declared 1 % tolerance (0.1 %); doubling both
  extents halves the eigenvalue and both wavenumbers exactly (the
  inverse-radius scaling at fixed shape); the value equals the
  configuration model's `taylor_eigenvalue_per_m()` bit for bit;
  non-positive extents are refused.
- **Relaxed-state field** (`field.py`; the separation form of the
  eigenvalue problem): on the midplane axis ``B_z = B0`` exactly and the
  other components vanish; at the wall ``B_r`` and ``B_theta`` vanish to
  `1e-15 B0` (the kernel's ``J1(j_{1,1})``); at both end plates ``B_z = 0``
  exactly (the kernel's exact phases); the three components of
  ``curl B`` equal ``lambda B`` and ``div B`` vanishes by central
  differences to `1e-6` relative; the axial phases equal the platform's
  sine and cosine to `1e-15` (a test-side cross-check, never used by the
  model); the grid layout is fixed (radial outermost); stations outside
  ``[0, 1]``, division counts that are not positive multiples of four and
  a non-positive axis field are refused.
- **Formation disposition** (`formation.py`; Wood 2005): hollow above
  ``1 + tolerance``, peaked below ``1 - tolerance``, relaxed inside with
  inclusive edges; at zero tolerance the peaked side coincides with the
  configuration model's advisory finding; inputs outside their domains
  are refused.
- A composed `Level0PhysicsRecord` (`scpn.spheromak-level0-physics.v1`
  `1.0.0`) with canonical bytes, SHA-256 digest, fixed non-claims and two
  pinned reference digests (relaxed and peaked), built from the validated
  configuration and explicit `ModelInputs` (axis field, radial stations,
  axial divisions, relaxed-band tolerance); every input is validated.
- **Native parity**: the Rust crate in `rust/` mirrors every kernel with
  identical operation order on the library's Rust crate at the pinned
  commit; `tests/test_physics_native_parity.py` compares float64 bit
  patterns for the eigenvalue of four geometries, the axial phases of
  three division counts, 560 field samples and four dispositions, plus
  the refusal paths of the bindings.
- **Benchmark**: `benchmarks/level0_physics.py` per the ecosystem
  benchmark standard; results in `docs/benchmarks.md` and the committed
  local artefact `benchmarks/results/level0_physics.local.json`.

Bounded claims — what is NOT claimed:

- Every number is a closed-form evaluation of the lowest axisymmetric
  relaxed state of an ideal cylindrical flux conserver on a synthetic
  configuration; no equilibrium reconstruction, stability, helicity
  balance or resistive decay is computed, and no eigenvalue problem is
  solved numerically (the eigenvalue is the closed form of the cylinder).
- The SSPX anchor reproduces one printed number within a declared
  tolerance; it is not a correlation with the machine's data. The
  cylindrical eigenvalue's own citation (Turner et al. 1983) is not on
  file; the separation form is derived here and the curl identity is
  tested numerically.
- The magnetic axis, the helicity–energy relation, the tilt criterion and
  the decay time are not evaluated (no filed source or kernel).
- The formation disposition restates a published operating rule against
  a declared tolerance; it predicts nothing about any discharge.
- No value describes, approximates or validates any real machine; the
  benchmark measures per-point evaluation cost of two implementations of
  the same closed forms, not physics.
- Maturity stays `computational_prototype`.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The nullable `timing_uncertainty_s` member, declared `null` on every
  channel because no event-relative candidate is applicable here; a
  non-null value is refused. This keeps the channel shape identical across
  the portfolio under envelope 1.1.0.
- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, and incomplete candidate coverage —
  every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: flux loops, Thomson profiles, surface probe array, synthetic oscillator, each bound to its clock domain.
- A documented advisory band check with its source stated in the code:
  spheromak tilt/shift and relaxation activity in the 1–200 kHz scale (Bellan 2000); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_spheromak_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; no `timing_marker` (no
  event-relative candidate is applicable); numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.
