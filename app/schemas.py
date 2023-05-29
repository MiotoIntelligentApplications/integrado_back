import datetime as _dt
import pydantic as _pydantic


class _VehicleOwnerBase(_pydantic.BaseModel):
    document: str
    email: str
    address: str
    state: str
    city: str
    phone: str


class VehicleOwnerCreate(_VehicleOwnerBase):
    hashed_password: str

    class Config:
        orm_mode = True


class VehicleOwner(_VehicleOwnerBase):
    id: int

    class Config:
        orm_mode = True


class _VehicleBase(_pydantic.BaseModel):
    license_plate: str
    license_plate_city: str
    license_plate_state: str
    v_type: str
    v_make: str
    v_model: str
    color: str
    year: int
    renavam: str
    chassis: str
    axles_number: int


class VehicleCreate(_VehicleBase):
    pass


class Vehicle(_VehicleBase):
    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        orm_mode = True
