from datetime import date

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    Target,
    Instrument,
    Observation,
    Spectrum,
    LineMeasurement,
)


def main() -> None:

    with SessionLocal() as session:

        # ---------------------------------------------------------
        # Check whether target already exists
        # ---------------------------------------------------------

        existing_target = session.scalar(
            select(Target).where(
                Target.source_name == "J000121.63+265009.17"
            )
        )

        if existing_target is not None:
            print("Target already exists.")
            return

        # ---------------------------------------------------------
        # Create target
        # ---------------------------------------------------------

        target = Target(
            source_name="J000121.63+265009.17",
            aliases=["J0001+2650"],
            ra_deg=0.340125,
            dec_deg=26.835880,
            redshift=5.75,
            object_type="quasar",
            discovery_survey="JWST follow-up",
            notes="High-redshift quasar with possible Halpha BAL absorption",
            metadata_json={
                "science_tags": [
                    "high-z",
                    "JWST",
                    "Halpha",
                    "BAL-candidate",
                ],
                "redshift_quality": "spectroscopic",
            },
        )

        # ---------------------------------------------------------
        # Create instrument
        # ---------------------------------------------------------

        instrument = Instrument(
            facility="JWST",
            telescope="JWST",
            instrument_name="NIRSpec G395H/F290LP",
            wavelength_min_ang=29000,
            wavelength_max_ang=52000,
            spectral_resolution="R~2700",
            metadata_json={
                "grating": "G395H",
                "filter": "F290LP",
            },
        )

        # ---------------------------------------------------------
        # Create observation
        # ---------------------------------------------------------

        observation = Observation(
            target=target,
            instrument=instrument,
            facility="JWST",
            obs_date=date(2024, 1, 12),
            mjd=60321,
            exposure_time_sec=5000,
            n_exposures=4,
            notes="JWST NIRSpec observation",
            metadata_json={
                "proposal_id": "5645",
                "grating": "G395H",
                "filter": "F290LP",
            },
        )

        # ---------------------------------------------------------
        # Create spectrum
        # ---------------------------------------------------------

        spectrum = Spectrum(
            target=target,
            observation=observation,
            spectrum_level="calibrated",
            filename="jw05645-o002_t002_nirspec_g395h-f290lp_x1d.fits",
            file_path="/data/jwst/jw05645-o002_t002_nirspec_g395h-f290lp_x1d.fits",
            wavelength_min_ang=29000,
            wavelength_max_ang=52000,
            snr_median=35.0,
            is_flux_calibrated=True,
            is_continuum_normalized=False,
            is_rest_frame=False,
            fits_header={
                "INSTRUME": "NIRSpec",
                "GRATING": "G395H",
                "FILTER": "F290LP",
                "EXPTIME": 5000,
            },
            reduction_metadata={
                "pipeline": "jwst",
                "product": "x1d",
                "calibration_level": 3,
            },
            notes="JWST x1d spectrum",
        )

        # ---------------------------------------------------------
        # Flush to get target_id
        # ---------------------------------------------------------

        session.add(target)
        session.flush()

        # ---------------------------------------------------------
        # Create line measurement
        # ---------------------------------------------------------

        measurement = LineMeasurement(
            target_id=target.target_id,
            spectrum=spectrum,
            line_name="Halpha absorption",
            line_type="broad_absorption",
            ew_ang=80.0,
            ew_error_ang=5.0,
            vmin_kms=-30000,
            vmax_kms=-5000,
            quality_flag="candidate",
            notes="Possible broad saturated Halpha absorption",
            metadata_json={
                "needs_check": [
                    "individual exposures",
                    "nods",
                    "2D spectrum",
                    "grating gap",
                ]
            },
        )

        session.add(measurement)

        # ---------------------------------------------------------
        # Commit everything
        # ---------------------------------------------------------

        session.commit()

        print("JWST target inserted successfully.")


if __name__ == "__main__":
    main()
