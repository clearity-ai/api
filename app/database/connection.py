import os

from sqlmodel import SQLModel, Session, create_engine
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

from app.models.user import User
from app.utils import get_secret

import pdb

# Define Cloud SQL connection variables
db_instance_connection_name = os.getenv("DB_INSTANCE_CONNECTION_NAME")
db_user = os.getenv("DB_USER")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
db_pass = get_secret(project_id, "DB_PASSWORD")
db_name = os.getenv("DB_NAME")
ip_type = IPTypes.PUBLIC


# Define Cloud SQL Python "creator" function for SQLAlchemy
def getconn() -> pg8000.dbapi.Connection:
    # Initialize Cloud SQL Python Connector object
    connector = Connector()
    conn = connector.connect(
        db_instance_connection_name,
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        ip_type=ip_type,
    )

    return conn


# Create SQLAlchemy Engine using the Cloud SQL Python Connector
engine = create_engine("postgresql+pg8000://", creator=getconn, echo=True)


def connect_to_db():
    # Whenever you create a class that inherits from SQLModel and is
    # configured with table = True, it is registered in this metadata attribute.
    # For that the class definitions have to be executed though
    # (e.g. importing User classes above)

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
