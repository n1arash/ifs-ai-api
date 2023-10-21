import enum
import datetime
import uuid as uuid_lib
from sqlmodel import SQLModel, Field, Column, DateTime, text

generate_uuid_sqlite = """(lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))))"""


class Role(enum.StrEnum):
    SYSTEM = "System"
    HUMAN = "Human"
    AI = "Ai"


class BaseModel(SQLModel):
    id: uuid_lib.UUID = Field(
        default_factory=uuid_lib.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={
            "server_default": text(f"{generate_uuid_sqlite}"),
            "unique": True
        }
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP")
        }
    )

    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP")
        }
    )
