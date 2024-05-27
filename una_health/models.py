from una_health import db


class GlucoseTrack(db.Model):
    __tablename__ = 'glucose_track'

    user_id = db.Column(db.String, primary_key=True, index=True)
    device_timestamp = db.Column(db.DateTime, primary_key=True, nullable=False)
    device = db.Column(db.String, nullable=False)
    serial_number = db.Column(db.String, nullable=False)
    recording_type = db.Column(db.Integer)
    glucose_level = db.Column(db.Float)

    def to_dict(self):
        return {key: val for key, val in self.__dict__.items() if not key.startswith('_')}

