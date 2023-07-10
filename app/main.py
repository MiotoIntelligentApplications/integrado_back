import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
from typing import List


app = _fastapi.FastAPI()


@app.get("/api")
async def root():
    return {"message": "Integrado API"}

@app.post("/api/vehicle_owners")
async def create_vehicle_owner(
    vehicle_owner: _schemas.VehicleOwnerCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_vehicle_owner = await _services.get_vehicle_owner_by_email(db=db, email=vehicle_owner.email)

    if db_vehicle_owner:
        raise _fastapi.HTTPException(status_code=400, detail="Email already registered")

    vehicle_owner = await _services.create_vehicle_owner(vehicle_owner, db)

    return _services.create_token(vehicle_owner)


@app.post("/api/token")
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    vehicle_owner = await _services.authenticate_vehicle_owner(
        email=form_data.username, password=form_data.password, db=db
    )

    if not vehicle_owner:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid credentials")

    return await _services.create_token(vehicle_owner)


@app.get("/api/vehicle_owners/me", response_model=_schemas.VehicleOwner)
async def get_vehicle_owner(vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner)):
    return vehicle_owner


@app.post("/api/vehicles", response_model=_schemas.Vehicle)
async def create_vehicle(
    vehicle: _schemas.VehicleCreate,
    vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.create_vehicle(vehicle_owner=vehicle_owner, vehicle=vehicle, db=db)


@app.get("/api/vehicles", response_model=List[_schemas.Vehicle])
async def get_vehicles(
    vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_vehicles(vehicle_owner=vehicle_owner, db=db)


@app.get("/api/vehicles/{vehicle_id}", status_code=200)
async def get_vehicle(
    vehicle_id: int,
    vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_vehicle(vehicle_id, vehicle_owner, db)


@app.delete("/api/vehicles/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: int,
    vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await _services.delete_vehicle(vehicle_id, vehicle_owner, db)
    return {"message", "Deletado com sucesso"}


@app.put("/api/vehicles/{vehicle_id}", status_code=200)
async def update_vehicle(
    vehicle_id: int,
    vehicle: _schemas.VehicleCreate,
    vehicle_owner: _schemas.VehicleOwner = _fastapi.Depends(_services.get_current_vehicle_owner),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await _services.update_vehicle(vehicle_id, vehicle, vehicle_owner, db)
    return {"message", "Editado com sucesso"}
