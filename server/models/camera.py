from database import db
import enum

class ModeEnum(enum.Enum):
    FORCED = 'FORCED',
    AUTO = "AUTO"

class StatusEnum(enum.Enum):
    ON = "ON"
    OFF = "OFF"
    DEFROST = "DEFROST"

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_temperature = db.Column(db.Float, nullable=False)
    defrost_threshold_temperature = db.Column(db.Float, nullable=False)
    defrost_type = db.Column(db.Enum(ModeEnum), default=ModeEnum.AUTO, nullable=False)
    compressor_on = db.Column(db.Boolean, default=False, nullable=False)
    ventilation_on = db.Column(db.Boolean, default=False, nullable=False)
    heater_on = db.Column(db.Boolean, default=False, nullable=False)
    auto_mode = db.Column(db.Boolean, default=True, nullable=False)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.OFF)
    problem = db.Column(db.Boolean, default=False)
    logs = db.relationship('CameraLog', backref='camera', cascade='all, delete-orphan')