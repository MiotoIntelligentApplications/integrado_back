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


async def get_user_by_email(db: _orm.Session, email: str):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    db_user = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password=password):
        return False

    return user


async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2_schema),
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = await get_user_by_email(db=db, email=payload.get("email"))

    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid credentials")

    return _schemas.User.from_orm(user)


async def create_lead(user: _schemas.User, lead: _schemas.LeadCreate, db: _orm.Session):
    db_lead = _models.Lead(**lead.dict(), owner_id=user.id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    return db_lead


async def get_leads(user: _schemas.User, db: _orm.Session):
    leads = db.query(_models.Lead).filter_by(owner_id=user.id)

    return list(map(_schemas.Lead.from_orm, leads))


async def _lead_selector(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = (
        db.query(_models.Lead)
        .filter_by(owner_id=user.id)
        .filter(_models.Lead.id == lead_id)
        .first()
    )

    if lead is None:
        raise _fastapi.HTTPException(status_code=404, detail="Lead does not exist")

    return lead


async def get_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id=lead_id, user=user, db=db)

    return _schemas.Lead.from_orm(lead)


async def delete_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id, user, db)

    db.delete(lead)
    db.commit()


async def update_lead(
    lead_id: int, lead: _schemas.LeadCreate, user: _schemas.User, db: _orm.Session
):
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(lead_db)

    return _schemas.Lead.from_orm(lead_db)
