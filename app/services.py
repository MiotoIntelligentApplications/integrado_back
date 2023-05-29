import os
import fastapi as _fastapi
import fastapi.security as _security
from dotenv import load_dotenv
import database as _database
import sqlalchemy.orm as _orm
import models as _models
import schemas as _schemas
import passlib.hash as _hash
import datetime as _dt
import jwt as _jwt


load_dotenv(".env")
JWT_SECRET = os.environ["JWT_SECRET"]

oauth2_schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_vehicle_owner_by_email(db: _orm.Session, email: str):
    return db.query(_models.VehicleOwner).filter(_models.VehicleOwner.email == email).first()


async def create_vehicle_owner(vehicle_owner: _schemas.VehicleOwnerCreate, db: _orm.Session):
    db_vehicle_owner = _models.VehicleOwner(
        document=vehicle_owner.document,
        email=vehicle_owner.email, 
        address=vehicle_owner.address,
        state=vehicle_owner.state,
        city=vehicle_owner.city,
        phone=vehicle_owner.phone,
        hashed_password=_hash.bcrypt.hash(vehicle_owner.hashed_password), 
    )
    db.add(db_vehicle_owner)
    db.commit()
    db.refresh(db_vehicle_owner)
    return db_vehicle_owner


async def authenticate_vehicle_owner(email: str, password: str, db: _orm.Session):
    vehicle_owner = await get_vehicle_owner_by_email(db=db, email=email)

    if not vehicle_owner:
        return False

    if not vehicle_owner.verify_password(password=password):
        return False

    return vehicle_owner


async def create_token(vehicle_owner: _models.VehicleOwner):
    vehicle_owner_obj = _schemas.VehicleOwner.from_orm(vehicle_owner)

    token = _jwt.encode(vehicle_owner_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_vehicle_owner(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2_schema),
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        vehicle_owner = await get_vehicle_owner_by_email(db=db, email=payload.get("email"))

    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid credentials")

    return _schemas.VehicleOwner.from_orm(vehicle_owner)


async def create_vehicle(vehicle_owner: _schemas.VehicleOwner, vehicle: _schemas.VehicleCreate, db: _orm.Session):
    db_vehicle = _models.Vehicle(**vehicle.dict(), owner_id=vehicle_owner.id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)

    return db_vehicle


async def get_vehicles(vehicle_owner: _schemas.VehicleOwner, db: _orm.Session):
    vehicles = db.query(_models.Vehicle).filter_by(owner_id=vehicle_owner.id)

    return list(map(_schemas.Vehicle.from_orm, vehicles))


async def _vehicle_selector(vehicle_id: int, vehicle_owner: _schemas.VehicleOwner, db: _orm.Session):
    vehicle = (
        db.query(_models.Vehicle)
        .filter_by(owner_id=vehicle_owner.id)
        .filter(_models.Vehicle.id == vehicle_id)
        .first()
    )

    if vehicle is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle does not exist")

    return vehicle


async def get_vehicle(vehicle_id: int, vehicle_owner: _schemas.VehicleOwner, db: _orm.Session):
    vehicle = await _vehicle_selector(vehicle_id=vehicle_id, vehicle_owner=vehicle_owner, db=db)

    return _schemas.Vehicle.from_orm(vehicle)


async def delete_vehicle(vehicle_id: int, vehicle_owner: _schemas.VehicleOwner, db: _orm.Session):
    vehicle = await _vehicle_selector(vehicle_id, vehicle_owner, db)

    db.delete(vehicle)
    db.commit()


async def update_vehicle(
    vehicle_id: int, vehicle: _schemas.VehicleCreate, vehicle_owner: _schemas.VehicleOwner, db: _orm.Session
):
    vehicle_db = await _vehicle_selector(vehicle_id, vehicle_owner, db)

    vehicle_db.license_plate = vehicle.license_plate
    vehicle_db.license_plate_city = vehicle.license_plate_city
    vehicle_db.license_plate_state = vehicle.license_plate_state
    vehicle_db.v_model = vehicle.v_model
    vehicle_db.v_type = vehicle.v_type
    vehicle_db.v_make = vehicle.v_make
    vehicle_db.year = vehicle.year
    vehicle_db.color = vehicle.color
    vehicle_db.renavam = vehicle.renavam
    vehicle_db.chassis = vehicle.chassis
    vehicle_db.axles_number = vehicle.axles_number
    vehicle_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(vehicle_db)

    return _schemas.Vehicle.from_orm(vehicle_db)
