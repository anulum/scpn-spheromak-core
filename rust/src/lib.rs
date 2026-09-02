// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Spheromak Core — native level-0 physics kernels

//! Native level-0 device-physics kernels of SCPN Spheromak Core.
//!
//! Every function mirrors one closed-form evaluation of the pure-Python
//! floor in `scpn_spheromak_core.physics` with the identical operation
//! order, so the IEEE-754 double results agree bit for bit. The kernels
//! use only `+`, `-`, `*`, `/` and `sqrt` (all correctly rounded) plus the
//! vendored Bessel functions and unit circle of the shared kernel library
//! crate (`scpn-reactor-kernels-rs`, pinned by commit in `Cargo.toml` and
//! in the manifest), which the Python floor evaluates through the same
//! library. Nothing here solves an equation and no value describes a real
//! machine; the design records are ADR 0005 and ADR 0006 of the
//! repository.

pub mod eigenvalue;
pub mod field;
pub mod formation;

pub use scpn_reactor_kernels_native::numerics::transcendental::NumericsError;

#[cfg(feature = "python")]
mod python {
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;

    fn numerics(err: crate::NumericsError) -> PyErr {
        PyValueError::new_err(err.to_string())
    }

    /// Eigenvalue tuple, see `crate::eigenvalue::taylor_eigenvalue`.
    #[pyfunction]
    fn taylor_eigenvalue(radius_m: f64, length_m: f64) -> PyResult<(f64, f64, f64)> {
        let e = crate::eigenvalue::taylor_eigenvalue(radius_m, length_m).map_err(numerics)?;
        Ok((
            e.radial_wavenumber_per_m,
            e.axial_wavenumber_per_m,
            e.eigenvalue_per_m,
        ))
    }

    /// Axial phases, see `crate::field::axial_phases`.
    #[pyfunction]
    fn axial_phases(divisions: usize) -> PyResult<Vec<(f64, f64)>> {
        let phases = crate::field::axial_phases(divisions).map_err(numerics)?;
        Ok(phases.iter().map(|p| (p[0], p[1])).collect())
    }

    /// Field sample tuple, see `crate::field::field_sample`.
    #[pyfunction]
    #[allow(clippy::too_many_arguments)]
    fn field_sample(
        radial_fraction: f64,
        axial_fraction: f64,
        cosine: f64,
        sine: f64,
        radius_m: f64,
        length_m: f64,
        axis_field_t: f64,
    ) -> PyResult<(f64, f64, f64, f64, f64, f64, f64)> {
        let eigen = crate::eigenvalue::taylor_eigenvalue(radius_m, length_m).map_err(numerics)?;
        let s = crate::field::field_sample(
            radial_fraction,
            axial_fraction,
            cosine,
            sine,
            &eigen,
            axis_field_t,
        )
        .map_err(numerics)?;
        Ok((
            s.radial_fraction,
            s.axial_fraction,
            s.radius_m,
            s.height_m,
            s.radial_field_t,
            s.azimuthal_field_t,
            s.axial_field_t,
        ))
    }

    /// Formation disposition tuple, see `crate::formation::formation_disposition`.
    #[pyfunction]
    fn formation_disposition(
        gun_lambda_per_m: f64,
        eigenvalue_per_m: f64,
        tolerance: f64,
    ) -> PyResult<(f64, f64, f64, f64, String)> {
        let d =
            crate::formation::formation_disposition(gun_lambda_per_m, eigenvalue_per_m, tolerance)
                .map_err(numerics)?;
        Ok((
            d.gun_lambda_per_m,
            d.eigenvalue_per_m,
            d.ratio,
            d.relaxed_ratio_tolerance,
            d.disposition.to_string(),
        ))
    }

    /// Python module `scpn_spheromak_native`.
    #[pymodule]
    fn scpn_spheromak_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(taylor_eigenvalue, m)?)?;
        m.add_function(wrap_pyfunction!(axial_phases, m)?)?;
        m.add_function(wrap_pyfunction!(field_sample, m)?)?;
        m.add_function(wrap_pyfunction!(formation_disposition, m)?)?;
        Ok(())
    }
}
