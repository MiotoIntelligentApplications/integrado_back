import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import database as _database


class VehicleOwner(_database.Base):
    __tablename__ = "vehicle_owners"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    document = _sql.Column(_sql.String, unique=True, index=True)
    email = _sql.Column(_sql.String, unique=True, index=True)
    address = _sql.Column(_sql.String, index=True)
    state = _sql.Column(_sql.String, index=True)
    city = _sql.Column(_sql.String, index=True)
    phone = _sql.Column(_sql.String, index=True)
    hashed_password = _sql.Column(_sql.String)

    vehicles = _orm.relationship("Vehicle", back_populates="owner")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)
    

class Vehicle(_database.Base):
    __tablename__ = "vehicles"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("vehicle_owners.id"))
    license_plate = _sql.Column(_sql.String, index=True)
    license_plate_city = _sql.Column(_sql.String, index=True)
    license_plate_state = _sql.Column(_sql.String, index=True)
    v_type = _sql.Column(_sql.String, index=True)
    v_make = _sql.Column(_sql.String, index=True)
    color = _sql.Column(_sql.String, index=True)
    year = _sql.Column(_sql.Integer, index=True)
    renavam = _sql.Column(_sql.String, index=True)
    chassi = _sql.Column(_sql.String, index=True)
    axles_number = _sql.Column(_sql.Integer, index=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    date_last_updated = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

    owner = _orm.relationship("VehicleOwner", back_populates="vehicles")
