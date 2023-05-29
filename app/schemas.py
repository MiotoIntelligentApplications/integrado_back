import datetime as _dt
import pydantic as _pydantic


class _VehicleOwnerBase(_pydantic.BaseModel):
    email: str


class VehicleOwnerCreate(_VehicleOwnerBase):
    hashed_password: str

    class Config:
        orm_mode = True


class VehicleOwner(_VehicleOwnerBase):
    id: int

    class Config:
        orm_mode = True


class _VehicleBase(_pydantic.BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str


class VehicleCreate(_VehicleBase):
    pass


class Vehicle(_VehicleBase):
    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        orm_mode = True
