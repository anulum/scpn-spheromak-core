<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Spheromak Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics: the cylindrical relaxed state with native parity

Status: accepted (2026-09-02). Adds the third implemented capability,
`level0_device_physics`, at `computational_prototype`.

## Context

Until this record the repository carried no physics beyond the
configuration model's cylindrical Taylor eigenvalue and its gun-threshold
advisory. Every device manifest excludes
`solver_mathematics_and_validation_evidence` (owner SCPN-FUSION-CORE), and
no FUSION seam covers the spheromak family. The device owner therefore
needs its own bounded, exercised, published physics: closed forms from
the family's own literature, evaluated on the validated configuration,
without solving any equation. Three freely available sources fix the
model: the SSPX operation report (R. D. Wood et al., UCRL-JRNL-214703
(2005), OSTI 883741: the flux-conserver eigenvalue `lambda_FC = 9.9 m^-1`
of a "1 m diameter by 0.5 m high" conserver, `lambda_gun = mu0 I_gun /
psi_gun` as the figure of merit, and the hollow/peaked/relaxed
dispositions), the reactor-opportunities study (E. B. Hooper et al.
(2003), OSTI 15005037: the eigenvalue is the homogeneous solution of
`curl B = lambda_fc B` in the flux conserver) and the S-1 Taylor-state
verification (PPPL-2257 (1985), OSTI 5141825: at fixed shape the
eigenvalue is inversely proportional to the radius). The cylindrical
eigenvalue's own citation (Turner et al. 1983) and Bellan's monograph are
not freely available; the separation form is derived here and anchored to
the printed SSPX number.

## Decision

1. A new owned domain `analytic_device_physics_models` is declared in
   `reactor-domain.json`: device-owned closed-form and 0-D models from the
   device literature. It is disjoint from solver mathematics: no solver
   code is copied, no equilibrium reconstruction, stability, helicity
   balance or decay equation is solved, and no FUSION seam is implied or
   consumed.
2. Three models, each with its published form cited in the module
   docstring, live one per module under `src/scpn_spheromak_core/physics/`:
   the Taylor eigenvalue (`eigenvalue.py`: `k_r = j_{1,1} / R`,
   `k_z = pi / L`, `lambda_fc = sqrt(k_r^2 + k_z^2)`), the
   Chandrasekhar–Kendall field of that state (`field.py`:
   `B_z = B0 J0(k_r r) sin(k_z z)`, `B_theta = B0 (lambda / k_r) J1(k_r r)
   sin(k_z z)`, `B_r = -B0 (k_z / k_r) J1(k_r r) cos(k_z z)` on a declared
   grid) and the formation disposition (`formation.py`:
   `lambda_gun / lambda_fc` classified hollow, peaked or relaxed against a
   declared tolerance). A composed `Level0PhysicsRecord` serialises
   canonically with a SHA-256 digest and carries fixed non-claims.
3. The configuration model's constant `3.832` is replaced by the shared
   kernel library's correctly rounded `j_{1,1}` (a data change of the
   configuration model, recorded in ADR 0002's addendum and the changelog;
   the eigenvalue of any configuration changes in the fourth significant
   figure) and its evaluation is written as `sqrt(k_r k_r + k_z k_z)` so
   the level-0 physics reproduces it bit for bit.
4. No platform trigonometric function is called: the axial stations are
   `z = k L / N` with `N` a multiple of four, and their phases
   `(cos(pi k / N), sin(pi k / N))` are the first `N + 1` points of the
   library's unit circle with `2 N` segments (exact `0` and `±1` at the
   plates and the midplane by the kernel's symmetry). The magnetic axis
   `r = j'_{1,1} / k_r` is not evaluated because the first zero of
   `J1'` is not in the library; the helicity–energy relation, the tilt
   criterion and the resistive decay time are not implemented because no
   filed source states them (recorded blockers).
5. Inputs the configuration does not carry are declared explicitly in
   `ModelInputs` (the midplane axis field `B0`, the radial stations, the
   axial divisions and the relaxed-band tolerance); nothing is defaulted
   silently and every input is refused outside its domain, never clamped.
6. The Bessel functions and the unit circle are the pinned shared kernel
   library's (ADR 0006); the Python floor uses only `+ - * /`, `sqrt` and
   those kernels. Native kernels (`rust/`, crate `scpn-spheromak-rs`,
   optional distribution `scpn-spheromak-native` via maturin) mirror every
   evaluation with identical operation order on the library's Rust crate;
   parity tests compare float64 bit patterns, never tolerances. The
   pure-Python floor remains the public API and the default.
7. Performance numbers follow the ecosystem benchmark standard; the local
   artefact is committed and labelled non-isolated.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty. VALIDATION states per model what is exercised and what is
not claimed: the SSPX eigenvalue is reproduced within a declared 1 %
(9.91 against 9.9), the inverse-radius scaling is exact, the field meets
the conducting wall and the end plates and satisfies `curl B = lambda B`
and `div B = 0` by central differences to `1e-6`, and the formation
disposition at zero tolerance coincides with the configuration model's
advisory. None of this is a correlation with data. The manifest change
alters `manifest_sha256` inside the plan envelope, so the envelope
fixture is regenerated from the public surface and re-pinned; the plan
bytes and `plan_sha256` are unchanged.
