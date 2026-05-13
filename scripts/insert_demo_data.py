from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Target, Instrument, Observation, Spectrum, LineMeasurement


def main() -> None:
    with SessionLocal() as session:
        try:
            existing = session.scalar(
                select(Target).where(Target.source_name == "SDSS J1333+0012")
            )

            if existing is not None:
                print("Demo target already exists. Skipping insert.")
                return

            target = Target(
                source_name="SDSS J1333+0012",
                aliases=["J1333+0012", "SDSS J133356.02+001229.1"],
                ra_deg=203.4834,
                dec_deg=0.2081,
                redshift=0.9197,
                object_type="bal_quasar",
                discovery_survey="SDSS",
                notes="Periodic Mg II BAL variability candidate",
                metadata_json={
                    "science_tags": ["BAL", "MgII", "variability", "periodicity"],
                    "priority": "high",
                },
            )

            instrument = Instrument(
                facility="SDSS",
                telescope="Sloan 2.5m",
                instrument_name="BOSS/eBOSS Spectrograph",
                wavelength_min_ang=3600,
                wavelength_max_ang=10400,
                spectral_resolution="R~2000",
                metadata_json={"survey": "SDSS"},
            )

            observation = Observation(
                target=target,
                instrument=instrument,
                facility="SDSS",
                obs_date=date(2001, 2, 15),
                mjd=51955,
                exposure_time_sec=3600,
                n_exposures=1,
                notes="Reference SDSS spectrum",
                metadata_json={"plate": 298, "fiber": 467},
            )

            spectrum = Spectrum(
                target=target,
                observation=observation,
                spectrum_level="calibrated",
                filename="spec-0298-51955-0467.fits",
                file_path="/data/sdss/spec-0298-51955-0467.fits",
                wavelength_min_ang=3600,
                wavelength_max_ang=10400,
                snr_median=25.0,
                is_flux_calibrated=True,
                is_continuum_normalized=False,
                is_rest_frame=False,
                fits_header={
                    "PLATE": 298,
                    "MJD": 51955,
                    "FIBERID": 467,
                },
                reduction_metadata={
                    "pipeline": "SDSS spectro pipeline",
                    "version": "DR16",
                },
                notes="Reference SDSS spectrum",
            )

            session.add(target)
            session.flush()

            measurement = LineMeasurement(
                target_id=target.target_id,
                spectrum=spectrum,
                line_name="MgII BAL",
                line_type="broad_absorption",
                ew_ang=15.2,
                ew_error_ang=1.1,
                vmin_kms=-18000,
                vmax_kms=-3000,
                quality_flag="good",
                notes="Strong MgII BAL absorption",
                metadata_json={
                    "component": "B_total",
                    "continuum_method": "PyQSOFit reference continuum",
                },
            )

            session.add(measurement)
            session.commit()

            print("Demo data inserted successfully.")

        except IntegrityError as exc:
            session.rollback()
            print("Integrity error. Data may already exist.")
            print(exc)

        except Exception as exc:
            session.rollback()
            print("Unexpected error.")
            print(exc)


if __name__ == "__main__":
    main()
