from sqlmodel import SQLModel, Session
from .engine import engine


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session