<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Spheromak Core — ADR 0007
-->

# ADR 0007 — Device 3D model and device CAD model on the shared geometry and CAD kernels

Status: accepted (2026-09-03). Adds the fourth and fifth implemented
capabilities, `device_3d_model` and `device_cad_model`, at
`computational_prototype`.

## Context

The repository owns device truth for the spheromak family: the validated
configuration carries the flux-conserver bore and length and the
formation source (ADR 0002), and the level-0 models evaluate the relaxed
state in that cylinder (ADR 0005, ADR 0006). There was no mechanical
envelope and no way to present, measure or hand a design to downstream
tooling. The research group's G1/G2 pattern (the Z-PINCH pilot and the
theta-pinch backfill) fixes how a family gains it: a device-owned
geometry record, the analytic-surface model on the shared geometry
kernels, and the B-rep model of the same bodies on the shared CAD kernels
with the library's per-body evidence.

## Decision

1. `DeviceGeometry` carries the device-owned mechanical envelope the
   configuration does not: the conserver wall thickness, the coaxial gun
   electrodes (inner radius, outer bore and wall) and gun length below the
   conserver, and the end-wall thickness. The conserver bore and length
   are the configuration's own values, used directly — never duplicated.
2. Five bodies in a fixed order on the device axis (the gun below the
   conserver, which spans z = 0 to L): gun inner electrode, gun outer
   electrode, flux conserver, conserver end wall, plasma column. The
   layout follows Wood et al. (UCRL-JRNL-214703, 2005): the gun outer
   electrode is contiguous with the conserver bore, enforced fail-closed
   (its outer radius must equal the configuration's conserver radius
   exactly). The plasma body is the cylindrical relaxed-state domain of
   the level-0 models, not the toroidal equilibrium shape; the printed
   minor/major radii of the source machine are deliberately not modelled
   at this tier.
3. Tier G1: `DeviceModel3D` (`scpn.spheromak-3d-model.v1` 1.0.0) on the
   library's tessellation primitives with the closed-mesh contract; the
   exports are the library's serialisers with the device provenance as
   the GLB document extras. Tier G2: `DeviceModelCAD`
   (`scpn.spheromak-cad-model.v1` 1.0.0) on the library's `cad` group
   (`cad_brep_solids`, `cad_step_export`, `cad_faceting`) with the
   library's `cad_evidence` kernel checking every body fail-closed
   (B-rep against the analytic closed forms within 1e-9, faceted volume
   within the declared deflection deficit bound and the exact
   polygon-deficit bound of the G1 reference mesh); the STEP export is
   the library's normalised deterministic writer and `write_step` writes
   exactly the digested bytes.
4. The kernel-library pin moves to the commit carrying the CAD group, the
   evidence kernel and the placement kernels (0f76b8ca); the manifest's
   `kernel_library` block records it with the inventory digest at that
   commit and the consumed kernel identifiers (the four geometry kernels,
   the three CAD kernels, the evidence kernel, and `numerics_bessel`,
   which the level-0 physics continues to consume). The dependency gains
   the optional `cad` extra; the CI gains a `cad` job that installs the
   system library the mesher's wheel links against before the extra; the
   crate re-locks its `scpn-reactor-kernels-rs` dependency at the same
   commit and gains the group's documentation lints with `cargo doc` in
   the rust gate.
5. An anchor fixture carries the conserver dimensions the layout source
   prints (one metre diameter, half a metre height); tests at both tiers
   prove the printed dimensions appear in the built bodies. Reproducing a
   printed dimension is an anchor, never a claim about that machine.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty; the excluded domain
`shared_physics_geometry_and_numerics_kernels` already names the library.
The STEP file is an export of the record, never its source; determinism
of the STEP bytes is claimed within the pinned back-end environment only
(the record carries the back-end versions), and a back-end bump re-pins
the record digest as a governed data change. A change of the library pin
is a governed data change of this repository (manifest, descriptor and
inventory regeneration, envelope fixture re-pin, SPO re-intake). The
gun–conserver junction and feed-through hardware stay unmodelled at this
tier; the toroidal plasma shape waits for the torus-segment primitive in
the library and a later tier.
