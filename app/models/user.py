from sqlmodel import SQLModel, Field, UniqueConstraint
from datetime import datetime, date
from typing import Optional


class UserSignin(SQLModel):
    email: str
    password: str


class UserSignup(UserSignin):
    username: str
    sex: str
    birthdate: date


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("username"),
    )

    # ID is optional in our code but will always be created when saved to the db
    # (https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/)
    id: Optional[str] = Field(default=None, primary_key=True)
    email: str
    username: str
    sex: str
    birthdate: date
    date_created: Optional[date] = datetime.today().strftime("%Y-%m-%d")
    date_deleted: Optional[date] = None
    profile_picture: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "email": "gmoharram@gmail.com",
                "username": "gana",
                "sex": "female",
                "birthdate": "2000-09-13",
                "date_created": "2024-03-13",
                "date_deleted": None,
                "prfile_picture": None,
            }
        }


class UserUpdate(SQLModel):
    username: Optional[str]
    sex: Optional[str]
    birthdate: Optional[date]
    profile_picture: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "username": "Abed",
                "sex": "male",
                "birthdate": "2000-02-01",
                "profile_picture": None,
            }
        }
