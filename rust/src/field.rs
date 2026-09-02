// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Spheromak Core — relaxed-state field kernels

//! The Chandrasekhar–Kendall field of the relaxed state on the declared
//! grid, operation-for-operation identical to
//! `scpn_spheromak_core.physics.field`.

use crate::eigenvalue::TaylorEigenvalue;
use crate::NumericsError;
use scpn_reactor_kernels_native::geometry::trig::unit_circle;
use scpn_reactor_kernels_native::numerics::bessel::{bessel_j0, bessel_j1, BESSEL_J1_FIRST_ZERO};

/// Smallest admissible number of axial divisions.
pub const MIN_AXIAL_DIVISIONS: usize = 4;
/// The axial divisions must be a multiple of this.
pub const AXIAL_DIVISION_MULTIPLE: usize = 4;

/// The field at one grid station.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FieldSample {
    /// `r / R`.
    pub radial_fraction: f64,
    /// `z / L`.
    pub axial_fraction: f64,
    /// `r`.
    pub radius_m: f64,
    /// `z`.
    pub height_m: f64,
    /// `B_r`.
    pub radial_field_t: f64,
    /// `B_theta`.
    pub azimuthal_field_t: f64,
    /// `B_z`.
    pub axial_field_t: f64,
}

/// Refuse a radial station outside `[0, 1]`.
///
/// # Errors
/// Returns [`NumericsError`] naming the field and the bound.
pub fn require_radial_station(name: &str, fraction: f64) -> Result<f64, NumericsError> {
    if !fraction.is_finite() {
        return Err(NumericsError {
            message: format!("{name}: must be finite, got {fraction:?}"),
        });
    }
    if !(0.0..=1.0).contains(&fraction) {
        return Err(NumericsError {
            message: format!("{name}: a radial station is r / R within [0, 1], got {fraction:?}"),
        });
    }
    Ok(fraction)
}

/// Refuse an axial division count below four or not a multiple of four.
///
/// # Errors
/// Returns [`NumericsError`] naming the bound.
pub fn require_axial_divisions(divisions: usize) -> Result<usize, NumericsError> {
    if divisions < MIN_AXIAL_DIVISIONS {
        return Err(NumericsError {
            message: format!(
                "axial_divisions: must be at least {MIN_AXIAL_DIVISIONS}, got {divisions}"
            ),
        });
    }
    if divisions % AXIAL_DIVISION_MULTIPLE != 0 {
        return Err(NumericsError {
            message: format!(
                "axial_divisions: must be a multiple of {AXIAL_DIVISION_MULTIPLE}, got {divisions}"
            ),
        });
    }
    Ok(divisions)
}

/// `(cos, sin)` of `pi k / N` for `k = 0 ..= N` from the library's unit circle.
///
/// # Errors
/// Refuses an invalid division count.
pub fn axial_phases(divisions: usize) -> Result<Vec<[f64; 2]>, NumericsError> {
    let count = require_axial_divisions(divisions)?;
    let circle = unit_circle(2 * count).map_err(|err| NumericsError {
        message: err.to_string(),
    })?;
    Ok(circle[..=count].to_vec())
}

/// Evaluate the field at one station.
///
/// # Errors
/// Refuses a radial station outside `[0, 1]` or a non-positive axis field,
/// and propagates the library's refusal.
pub fn field_sample(
    radial_fraction: f64,
    axial_fraction: f64,
    cosine: f64,
    sine: f64,
    eigenvalue: &TaylorEigenvalue,
    axis_field_t: f64,
) -> Result<FieldSample, NumericsError> {
    require_radial_station("radial_fraction", radial_fraction)?;
    if !axis_field_t.is_finite() {
        return Err(NumericsError {
            message: format!("axis_field_t: must be finite, got {axis_field_t:?}"),
        });
    }
    if axis_field_t <= 0.0 {
        return Err(NumericsError {
            message: format!("axis_field_t: must be strictly positive, got {axis_field_t:?}"),
        });
    }
    let argument = BESSEL_J1_FIRST_ZERO * radial_fraction;
    let j0 = bessel_j0(argument)?;
    let j1 = bessel_j1(argument)?;
    let radial_ratio = eigenvalue.eigenvalue_per_m / eigenvalue.radial_wavenumber_per_m;
    let axial_ratio = eigenvalue.axial_wavenumber_per_m / eigenvalue.radial_wavenumber_per_m;
    Ok(FieldSample {
        radial_fraction,
        axial_fraction,
        radius_m: radial_fraction * eigenvalue.radius_m,
        height_m: axial_fraction * eigenvalue.length_m,
        radial_field_t: -(axis_field_t * axial_ratio * j1 * cosine),
        azimuthal_field_t: axis_field_t * radial_ratio * j1 * sine,
        axial_field_t: axis_field_t * j0 * sine,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::eigenvalue::taylor_eigenvalue;

    #[test]
    fn midplane_axis_and_plates() {
        let eigen = taylor_eigenvalue(0.5, 0.5).unwrap();
        let phases = axial_phases(4).unwrap();
        assert_eq!(phases.len(), 5);
        assert_eq!(phases[2], [0.0, 1.0]);
        let axis = field_sample(0.0, 0.5, phases[2][0], phases[2][1], &eigen, 0.2).unwrap();
        assert_eq!(axis.axial_field_t, 0.2);
        assert_eq!(axis.azimuthal_field_t, 0.0);
        let plate = field_sample(0.5, 0.0, phases[0][0], phases[0][1], &eigen, 0.2).unwrap();
        assert_eq!(plate.axial_field_t, 0.0);
        assert!(axial_phases(6).is_err());
        assert!(field_sample(1.5, 0.0, 1.0, 0.0, &eigen, 0.2).is_err());
        assert!(field_sample(0.5, 0.0, 1.0, 0.0, &eigen, 0.0).is_err());
    }
}
