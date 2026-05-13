from sqlalchemy import select

from app.database import SessionLocal
from app.models import Target, Observation, Spectrum, LineMeasurement


def main() -> None:
    session = SessionLocal()

    try:
        stmt = (
            select(
                Target.source_name,
                Target.redshift,
                Observation.mjd,
                Observation.facility,
                Spectrum.filename,
                LineMeasurement.line_name,
                LineMeasurement.ew_ang,
                LineMeasurement.ew_error_ang,
            )
            .join(Observation, Observation.target_id == Target.target_id)
            .join(Spectrum, Spectrum.observation_id == Observation.observation_id)
            .join(LineMeasurement, LineMeasurement.spectrum_id == Spectrum.spectrum_id)
            .where(Target.source_name == "SDSS J1333+0012")
            .order_by(Observation.mjd)
        )

        results = session.execute(stmt).all()

        for row in results:
            print(row)

    finally:
        session.close()


if __name__ == "__main__":
    main()
