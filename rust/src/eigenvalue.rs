// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Spheromak Core — Taylor eigenvalue kernel

//! The cylindrical Taylor eigenvalue of the flux conserver,
//! operation-for-operation identical to
//! `scpn_spheromak_core.physics.eigenvalue`.

use crate::NumericsError;
use scpn_reactor_kernels_native::numerics::bessel::BESSEL_J1_FIRST_ZERO;

/// `pi` as the Python floor's `math.pi`.
pub const PI: f64 = std::f64::consts::PI;

/// The eigenvalue and its wavenumbers.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TaylorEigenvalue {
    /// `R`.
    pub radius_m: f64,
    /// `L`.
    pub length_m: f64,
    /// `k_r = j_{1,1} / R`.
    pub radial_wavenumber_per_m: f64,
    /// `k_z = pi / L`.
    pub axial_wavenumber_per_m: f64,
    /// `sqrt(k_r^2 + k_z^2)`.
    pub eigenvalue_per_m: f64,
}

fn require_positive(name: &str, value: f64) -> Result<f64, NumericsError> {
    if !value.is_finite() {
        return Err(NumericsError {
            message: format!("{name}: must be finite, got {value:?}"),
        });
    }
    if value <= 0.0 {
        return Err(NumericsError {
            message: format!("{name}: must be strictly positive, got {value:?}"),
        });
    }
    Ok(value)
}

/// Evaluate the eigenvalue of a cylinder.
///
/// # Errors
/// Refuses a non-positive or non-finite extent.
pub fn taylor_eigenvalue(radius_m: f64, length_m: f64) -> Result<TaylorEigenvalue, NumericsError> {
    require_positive("radius_m", radius_m)?;
    require_positive("length_m", length_m)?;
    let radial = BESSEL_J1_FIRST_ZERO / radius_m;
    let axial = PI / length_m;
    Ok(TaylorEigenvalue {
        radius_m,
        length_m,
        radial_wavenumber_per_m: radial,
        axial_wavenumber_per_m: axial,
        eigenvalue_per_m: (radial * radial + axial * axial).sqrt(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sspx_anchor_and_scaling() {
        let sspx = taylor_eigenvalue(0.5, 0.5).unwrap();
        assert!((sspx.eigenvalue_per_m - 9.9).abs() / 9.9 < 0.01);
        let double = taylor_eigenvalue(1.0, 1.0).unwrap();
        assert_eq!(double.eigenvalue_per_m, sspx.eigenvalue_per_m / 2.0);
        assert!(taylor_eigenvalue(0.0, 1.0).is_err());
        assert!(taylor_eigenvalue(1.0, f64::NAN).is_err());
    }
}
