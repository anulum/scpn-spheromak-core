# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Spheromak Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the compact toroid inside its flux conserver, the
no-external-TF-coil hard invariant, and the lambda_gun versus
Taylor-eigenvalue formation threshold. The right-hand text panel states
only facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — poloidal section of the compact toroid inside
  its flux conserver with the formation gun (used by ``README.md``).
- ``repo_header_no_tf_invariant.png`` — the enforced hard invariant:
  external toroidal-field coils rejected, self-generated field accepted.
- ``repo_header_formation_threshold.png`` — the lambda_gun versus
  Taylor-eigenvalue formation gate.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "spheromak · compact toroid"),
    ("Hard Invariant", "no external TF coils · B_φ self-generated"),
    ("Formation Source", "λ_gun vs Taylor eigenvalue, flagged below"),
    ("Diagnostics & Clocks", "fail-closed vs pinned SPO catalogue"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.74,
        "SPHEROMAK",
        color="white",
        fontsize=30,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.685,
        "CORE",
        color="white",
        fontsize=30,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.625,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.585, 0.585], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.525
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _toroid_surfaces(
    ax: Any, centre_x: float, centre_z: float, scale: float = 1.0
) -> None:
    """Draw nested poloidal flux surfaces of a compact toroid."""
    theta = np.linspace(0.0, 2.0 * np.pi, 300)
    lobes = [(1.0, 1.9, 0.95), (0.72, 0.7, 0.4), (0.47, 0.7, 0.4), (0.24, 0.7, 0.4)]
    for side in (-1.0, +1.0):
        for fraction, lw, alpha in lobes:
            radius = fraction * 0.46 * scale
            x = centre_x + side * (0.52 * scale + radius * np.cos(theta) * 0.82)
            z = centre_z + radius * 1.55 * np.sin(theta) * (1.0 - 0.15 * np.cos(theta))
            ax.plot(x, z, color=CYAN, lw=lw, alpha=alpha)
        ax.plot(
            centre_x + side * 0.52 * scale,
            centre_z,
            ".",
            color=MAGENTA,
            ms=4,
            alpha=0.9,
        )


def generate_compact_toroid() -> None:
    """Generate ``repo_header.png``: the toroid in its flux conserver."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")

    grid_x = np.linspace(-1.6, 1.6, 200)
    grid_z = np.linspace(-1.1, 1.1, 160)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x / 1.25) ** 2 + (mesh_z / 0.85) ** 2)
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 2.2),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.8,
    )

    outline = np.linspace(0.0, 2.0 * np.pi, 400)
    can_x = 1.52 * np.sign(np.cos(outline)) * np.abs(np.cos(outline)) ** 0.55
    can_z = 1.02 * np.sign(np.sin(outline)) * np.abs(np.sin(outline)) ** 0.55
    ax.plot(can_x, can_z, color=STEEL, lw=2.4, alpha=0.85)
    ax.text(
        0,
        1.13,
        "flux conserver",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )

    _toroid_surfaces(ax, 0.0, 0.0, scale=1.35)

    ax.plot(-0.7, 0.0, "o", color="white", ms=5, alpha=0.9)
    ax.plot(0.7, 0.0, "x", color="white", ms=7, mew=1.6, alpha=0.9)
    ax.text(
        -0.7,
        -0.28,
        "B_φ ⊙",
        color="white",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.75,
    )
    ax.text(
        0.7,
        -0.28,
        "B_φ ⊗",
        color="white",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.75,
    )

    ax.add_patch(
        plt.Rectangle(
            (-0.34, -1.28),
            0.68,
            0.24,
            fill=False,
            ec=MAGENTA,
            lw=1.6,
            alpha=0.85,
        )
    )
    ax.annotate(
        "",
        xy=(0, -0.86),
        xytext=(0, -1.06),
        arrowprops={"arrowstyle": "->", "color": MAGENTA, "lw": 1.4, "alpha": 0.85},
    )
    ax.text(
        0.44,
        -1.2,
        "formation gun · λ_gun",
        color=MAGENTA,
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    ax.text(
        0,
        -1.44,
        "self-organised compact toroid · no centre column",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Compact Toroid, Self-Generated Field")
    _save(fig, plt, "repo_header.png")


def generate_no_tf_invariant() -> None:
    """Generate ``repo_header_no_tf_invariant.png``: the hard invariant."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    for index in range(8):
        angle = 2.0 * np.pi * index / 8
        coil_x = 2.3 + 1.35 * np.cos(angle)
        coil_z = 0.2 + 1.55 * np.sin(angle)
        ax.plot(
            coil_x + 0.30 * np.cos(theta),
            coil_z + 0.44 * np.sin(theta),
            color="#667788",
            lw=1.8,
            alpha=0.7,
        )
    ax.plot(
        2.3 + 0.95 * np.cos(theta),
        0.2 + 0.95 * np.sin(theta) * 0.75,
        color="#667788",
        lw=1.4,
        alpha=0.5,
    )
    ax.plot([1.05, 3.55], [-1.6, 2.0], color=RED, lw=2.6, alpha=0.9)
    ax.plot([1.05, 3.55], [2.0, -1.6], color=RED, lw=2.6, alpha=0.9)
    ax.text(
        2.3,
        -2.35,
        "external toroidal-field coils",
        color="#8899aa",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        2.3,
        -2.7,
        "REJECTED · hard invariant",
        color=RED,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    glow_x = np.linspace(5.6, 9.4, 140)
    glow_z = np.linspace(-1.6, 2.0, 120)
    mesh_x, mesh_z = np.meshgrid(glow_x, glow_z)
    rho = np.sqrt(((mesh_x - 7.5) / 1.35) ** 2 + ((mesh_z - 0.2) / 1.1) ** 2)
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 2.2),
        levels=24,
        cmap=_glow_cmap(),
        alpha=0.75,
    )
    _toroid_surfaces(ax, 7.5, 0.2, scale=1.5)
    ax.text(
        7.5,
        -2.35,
        "B_φ self-generated by the plasma",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        7.5,
        -2.7,
        "ACCEPTED · Bellan, Spheromaks (2000)",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot([4.85, 4.85], [-2.5, 2.6], color=STEEL, lw=0.8, alpha=0.4)
    _text_panel(fig, "No External TF Coils, By Construction")
    _save(fig, plt, "repo_header_no_tf_invariant.png")


def generate_formation_threshold() -> None:
    """Generate ``repo_header_formation_threshold.png``: the gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.4], [1.6, 1.6], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.6, 9.0], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.15,
        "λ_gun / λ_Taylor",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.75,
        "helicity delivered",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    x_threshold = 1.0 + (8.0 / 2.0) * 1.0
    ax.plot(
        [x_threshold, x_threshold],
        [1.6, 8.9],
        color=MAGENTA,
        lw=1.4,
        alpha=0.85,
        ls=(0, (5, 3)),
    )
    ax.text(
        x_threshold + 0.12,
        8.45,
        "λ_gun = λ_Taylor",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.95,
    )

    ax.fill_between([1.0, x_threshold], 1.6, 8.9, color=RED, alpha=0.05)
    ax.fill_between([x_threshold, 9.4], 1.6, 8.9, color=GREEN, alpha=0.05)
    ax.text(
        2.9,
        2.15,
        "flagged · no formation expected",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        7.35,
        2.15,
        "formation window",
        color=GREEN,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    lam = np.linspace(0.1, 2.0, 400)
    height = 1.6 + 6.6 / (1.0 + np.exp(-(lam - 1.0) * 6.0))
    xs = 1.0 + (8.0 / 2.0) * lam
    ax.plot(xs, height, color=CYAN, lw=2.4, alpha=0.95)

    _toroid_surfaces(ax, 7.6, 6.4, scale=1.15)
    ax.text(
        7.6,
        4.55,
        "compact toroid forms",
        color="#99bbdd",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.2,
        0.75,
        "declared λ_gun compared with the conserver Taylor eigenvalue",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Formation Gated By The Taylor Eigenvalue")
    _save(fig, plt, "repo_header_formation_threshold.png")


if __name__ == "__main__":
    generate_compact_toroid()
    generate_no_tf_invariant()
    generate_formation_threshold()
