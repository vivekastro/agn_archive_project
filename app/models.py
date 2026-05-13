from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    CheckConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Target(Base):
    __tablename__ = "targets"
    __table_args__ = (
        CheckConstraint("ra_deg >= 0 AND ra_deg < 360", name="check_ra_range"),
        CheckConstraint("dec_deg >= -90 AND dec_deg <= 90", name="check_dec_range"),
        CheckConstraint("redshift IS NULL OR redshift >= 0", name="check_redshift_positive"),
        UniqueConstraint("source_name", name="uq_target_source_name"),
        {"schema": "agn"},
    )

    target_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)

    ra_deg: Mapped[float] = mapped_column(Float, nullable=False)
    dec_deg: Mapped[float] = mapped_column(Float, nullable=False)
    redshift: Mapped[float | None] = mapped_column(Float, nullable=True)

    object_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    discovery_survey: Mapped[str | None] = mapped_column(String(100), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="target",
        cascade="all, delete-orphan",
    )

    spectra: Mapped[list["Spectrum"]] = relationship(
        back_populates="target",
        cascade="all, delete-orphan",
    )


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (
        {"schema": "agn"},
    )

    instrument_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    facility: Mapped[str] = mapped_column(String(50), nullable=False)
    telescope: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instrument_name: Mapped[str] = mapped_column(String(100), nullable=False)

    wavelength_min_ang: Mapped[float | None] = mapped_column(Float, nullable=True)
    wavelength_max_ang: Mapped[float | None] = mapped_column(Float, nullable=True)
    spectral_resolution: Mapped[str | None] = mapped_column(String(100), nullable=True)

    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    observations: Mapped[list["Observation"]] = relationship(back_populates="instrument")


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint("mjd > 0", name="check_mjd_positive"),
        CheckConstraint("exposure_time_sec IS NULL OR exposure_time_sec > 0", name="check_exptime_positive"),
        {"schema": "agn"},
    )

    observation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    target_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agn.targets.target_id", ondelete="CASCADE"),
        nullable=False,
    )

    instrument_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("agn.instruments.instrument_id"),
        nullable=True,
    )

    facility: Mapped[str] = mapped_column(String(50), nullable=False)
    obs_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    mjd: Mapped[float] = mapped_column(Float, nullable=False)

    exposure_time_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_exposures: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    target: Mapped["Target"] = relationship(back_populates="observations")
    instrument: Mapped["Instrument"] = relationship(back_populates="observations")

    spectra: Mapped[list["Spectrum"]] = relationship(
        back_populates="observation",
        cascade="all, delete-orphan",
    )


class Spectrum(Base):
    __tablename__ = "spectra"
    __table_args__ = (
        UniqueConstraint("filename", name="uq_spectrum_filename"),
        {"schema": "agn"},
    )

    spectrum_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    observation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agn.observations.observation_id", ondelete="CASCADE"),
        nullable=False,
    )

    target_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agn.targets.target_id", ondelete="CASCADE"),
        nullable=False,
    )

    spectrum_level: Mapped[str] = mapped_column(String(50), default="calibrated")

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    wavelength_min_ang: Mapped[float | None] = mapped_column(Float, nullable=True)
    wavelength_max_ang: Mapped[float | None] = mapped_column(Float, nullable=True)

    snr_median: Mapped[float | None] = mapped_column(Float, nullable=True)

    is_flux_calibrated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_continuum_normalized: Mapped[bool] = mapped_column(Boolean, default=False)
    is_rest_frame: Mapped[bool] = mapped_column(Boolean, default=False)

    fits_header: Mapped[dict] = mapped_column(JSONB, default=dict)
    reduction_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    target: Mapped["Target"] = relationship(back_populates="spectra")
    observation: Mapped["Observation"] = relationship(back_populates="spectra")

    line_measurements: Mapped[list["LineMeasurement"]] = relationship(
        back_populates="spectrum",
        cascade="all, delete-orphan",
    )


class LineMeasurement(Base):
    __tablename__ = "line_measurements"
    __table_args__ = (
        CheckConstraint("ew_ang IS NULL OR ew_ang >= 0", name="check_ew_positive"),
        {"schema": "agn"},
    )

    measurement_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    spectrum_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agn.spectra.spectrum_id", ondelete="CASCADE"),
        nullable=False,
    )

    target_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("agn.targets.target_id", ondelete="CASCADE"),
        nullable=False,
    )

    line_name: Mapped[str] = mapped_column(String(100), nullable=False)
    line_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    ew_ang: Mapped[float | None] = mapped_column(Float, nullable=True)
    ew_error_ang: Mapped[float | None] = mapped_column(Float, nullable=True)

    flux: Mapped[float | None] = mapped_column(Float, nullable=True)
    flux_error: Mapped[float | None] = mapped_column(Float, nullable=True)

    fwhm_kms: Mapped[float | None] = mapped_column(Float, nullable=True)
    vmin_kms: Mapped[float | None] = mapped_column(Float, nullable=True)
    vmax_kms: Mapped[float | None] = mapped_column(Float, nullable=True)

    quality_flag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    spectrum: Mapped["Spectrum"] = relationship(back_populates="line_measurements")
