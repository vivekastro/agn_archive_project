from flask import Blueprint, render_template, abort
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Target, Observation, Spectrum, LineMeasurement


bp = Blueprint("agn_archive", __name__)


@bp.route("/")
def index():
    with SessionLocal() as session:
        targets = session.scalars(
            select(Target).order_by(Target.source_name)
        ).all()

        return render_template("index.html", targets=targets)


@bp.route("/target/<int:target_id>")
def target_detail(target_id: int):
    with SessionLocal() as session:
        target = session.get(Target, target_id)

        if target is None:
            abort(404)

        spectra_stmt = (
            select(
                Spectrum.spectrum_id,
                Spectrum.filename,
                Spectrum.spectrum_level,
                Spectrum.wavelength_min_ang,
                Spectrum.wavelength_max_ang,
                Spectrum.snr_median,
                Observation.mjd,
                Observation.facility,
                Observation.obs_date,
            )
            .join(Observation, Observation.observation_id == Spectrum.observation_id)
            .where(Spectrum.target_id == target_id)
            .order_by(Observation.mjd)
        )

        spectra = session.execute(spectra_stmt).all()

        measurements_stmt = (
            select(
                LineMeasurement.measurement_id,
                LineMeasurement.line_name,
                LineMeasurement.line_type,
                LineMeasurement.ew_ang,
                LineMeasurement.ew_error_ang,
                LineMeasurement.vmin_kms,
                LineMeasurement.vmax_kms,
                LineMeasurement.quality_flag,
                Spectrum.filename,
                Observation.mjd,
                Observation.facility,
            )
            .join(Spectrum, Spectrum.spectrum_id == LineMeasurement.spectrum_id)
            .join(Observation, Observation.observation_id == Spectrum.observation_id)
            .where(LineMeasurement.target_id == target_id)
            .order_by(Observation.mjd, LineMeasurement.line_name)
        )

        measurements = session.execute(measurements_stmt).all()

        return render_template(
            "target_detail.html",
            target=target,
            spectra=spectra,
            measurements=measurements,
        )
