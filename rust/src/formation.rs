// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Spheromak Core — formation disposition kernel

//! The formation-source parameter against the eigenvalue (Wood et al.
//! 2005), operation-for-operation identical to
//! `scpn_spheromak_core.physics.formation`.

use crate::NumericsError;

/// `lambda_gun / lambda_fc` above `1 + tolerance`.
pub const DISPOSITION_HOLLOW: &str = "hollow";
/// Below `1 - tolerance`.
pub const DISPOSITION_PEAKED: &str = "peaked";
/// Within the band.
pub const DISPOSITION_RELAXED: &str = "relaxed";

/// The ratio and its disposition.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FormationDisposition {
    /// `lambda_gun`.
    pub gun_lambda_per_m: f64,
    /// `lambda_fc`.
    pub eigenvalue_per_m: f64,
    /// `lambda_gun / lambda_fc`.
    pub ratio: f64,
    /// The declared band half-width.
    pub relaxed_ratio_tolerance: f64,
    /// `hollow`, `peaked` or `relaxed`.
    pub disposition: &'static str,
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

/// Classify the source parameter against the eigenvalue.
///
/// # Errors
/// Refuses non-positive parameters and a tolerance outside `[0, 1)`.
pub fn formation_disposition(
    gun_lambda_per_m: f64,
    eigenvalue_per_m: f64,
    tolerance: f64,
) -> Result<FormationDisposition, NumericsError> {
    require_positive("gun_lambda_per_m", gun_lambda_per_m)?;
    require_positive("eigenvalue_per_m", eigenvalue_per_m)?;
    if !tolerance.is_finite() || !(0.0..1.0).contains(&tolerance) {
        return Err(NumericsError {
            message: format!("relaxed_ratio_tolerance: must be within [0, 1), got {tolerance:?}"),
        });
    }
    let ratio = gun_lambda_per_m / eigenvalue_per_m;
    let disposition = if ratio > 1.0 + tolerance {
        DISPOSITION_HOLLOW
    } else if ratio < 1.0 - tolerance {
        DISPOSITION_PEAKED
    } else {
        DISPOSITION_RELAXED
    };
    Ok(FormationDisposition {
        gun_lambda_per_m,
        eigenvalue_per_m,
        ratio,
        relaxed_ratio_tolerance: tolerance,
        disposition,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn three_dispositions() {
        assert_eq!(
            formation_disposition(12.0, 10.0, 0.1).unwrap().disposition,
            "hollow"
        );
        assert_eq!(
            formation_disposition(8.0, 10.0, 0.1).unwrap().disposition,
            "peaked"
        );
        assert_eq!(
            formation_disposition(10.5, 10.0, 0.1).unwrap().disposition,
            "relaxed"
        );
        assert!(formation_disposition(10.0, 10.0, 1.0).is_err());
        assert!(formation_disposition(0.0, 10.0, 0.1).is_err());
    }
}
