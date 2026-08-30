<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Spheromak Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)  
**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The spheromak is a compact toroid and
therefore superficially adjacent to both the FRC and the RFP; a boundary
decision was needed that separates these three self-organised
configurations cleanly.

## Decision

1. `SCPN-SPHEROMAK-CORE` owns exactly one registry configuration:
   `spheromak` (compact toroid).
2. The repository owns device-level truth only: relaxed compact-toroid
   configuration policy, coaxial-gun formation and helicity-injection
   sustainment semantics, pulsed lifecycle definitions, magnetics and
   helicity-balance diagnostic declarations, actuator-response model
   boundaries, the safety-envelope declaration (tilt/shift boundaries from
   the flux conserver), and the device-owned CONTROL adapter specification.
3. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One combined compact-toroid repository** (spheromak + FRC): rejected —
  the spheromak's comparable toroidal field, Taylor-relaxation physics,
  and helicity-injection driver differ from the FRC's negligible-toroidal-
  field, high-beta, theta-pinch-class formation on surfaces 1 and 2, and
  the portfolio map assigns them to different owners.
- **Folding the spheromak into the RFP repository** (both near-Taylor
  relaxed states): rejected — the simply connected geometry without a
  toroidal-field circuit, the gun-formation driver, and the flux-conserver
  stability model differ on surfaces 1, 2, and 4.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the spheromak
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future ADR
  records any such change here.
