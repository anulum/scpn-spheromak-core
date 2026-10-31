<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Spheromak Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns (`spheromak`). The claim
boundary and repository-level `evidence_maturity` semantics follow the
family pilot.

## Decision

1. The package `scpn_spheromak_core` implements the device
   configuration model as frozen, strictly typed value objects:
   cylindrical flux-conserver geometry, the formation source (gun
   current and bias poloidal flux), and the configuration container.
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard invariant: the configuration declares
   ``external_toroidal_field_coils`` and it must be false — the
   spheromak's toroidal field is self-generated, and the absence of
   external toroidal-field coils is a defining property of the class
   ("there are no toroidal magnetic field coils linking the plasma":
   R. D. Wood et al., UCRL-JRNL-214703 (2005), PDF p. 4).
4. Advisory estimates, reported by `consistency_report()` and never
   clamped: the Taylor-state eigenvalue of a cylindrical flux conserver
   ``lambda_fc = sqrt((3.832/R)^2 + (pi/L)^2)`` (first zero of J1;
   eigenvalue of ``curl B = lambda_fc B`` as defined in Hooper et al.
   2003, PDF p. 5) is compared with the source parameter
   ``lambda_gun = mu0 I_gun / Phi_bias`` (Wood et al. 2005, PDF p. 8);
   a source below the flux-conserver eigenvalue is flagged. Taking the
   eigenvalue as the formation threshold is a declared modelling choice
   (see the 2026-10-31 addendum).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (magnetics/helicity diagnostic semantics, safety
  envelope) build on these types; maturity advances per capability only
  with the evidence the family standard requires.

## Addendum (2026-09-02) — the Bessel zero is the shared library's constant

The literal `3.832` of the cylindrical Taylor eigenvalue is replaced by the
correctly rounded first zero of `J1` carried by the pinned shared kernel
library (`3.8317059702075125`, OEIS A115369; ADR 0006), and the eigenvalue
is evaluated as `sqrt(k_r k_r + k_z k_z)` so the level-0 physics (ADR 0005)
reproduces it bit for bit. The eigenvalue of any configuration changes in
the fourth significant figure; the advisory's direction is unchanged for
every exercised fixture. The applicability bounds and non-claims of this
record are unchanged.

## Addendum (2026-10-31) — credits bound to filed sources

The class invariant, the eigenvalue and the formation-source parameter
were credited to P. M. Bellan, Spheromaks (Imperial College Press, 2000),
which is not on file; no page of it was read for them. They are now bound
to the filed SSPX reports: Wood et al. (2005) PDF p. 4 (no toroidal-field
coils link the plasma) and p. 8 (``λgun=µ0Igun/ψgun``), and Hooper et al.
(2003) PDF p. 5 (the eigenvalue of ``curl B = λ_fc B``, with SSPX run so
that ``λ_gun`` is close to it). The filed Romero-Talamás et al. (2005)
report prints a geometry-dependent ejection threshold
``I_cr ~ 15 φ_0/µ_0`` (PDF p. 7), so flagging a source below the
eigenvalue is a declared modelling choice, and the finding now says
"declared threshold". No invariant, formula or threshold value changed.
