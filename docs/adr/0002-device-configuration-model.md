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
   (P. M. Bellan, Spheromaks, Imperial College Press, 2000).
4. Advisory estimates, reported by `consistency_report()` and never
   clamped: the Taylor-state eigenvalue of a cylindrical flux conserver
   ``lambda_fc = sqrt((3.832/R)^2 + (pi/L)^2)`` (first zero of J1;
   Bellan 2000, ch. 3) is compared with the source parameter
   ``lambda_gun = mu0 I_gun / Phi_bias``; a source below the
   flux-conserver eigenvalue is flagged because spheromak formation is
   not expected below the threshold (Bellan 2000, ch. 4).
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
