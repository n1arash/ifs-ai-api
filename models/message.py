from typing import Optional
from uuid import UUID

from models.base import BaseModel, Role
from sqlmodel import Field, Column, String, Relationship
from sqlalchemy_utils import ChoiceType


class Message(BaseModel, table=True):
    __tablename__ = "messages"
    role: Role = Field(sa_column=Column(ChoiceType(Role, impl=String()), nullable=False))
    content: str
    interaction_id: Optional[UUID] = Field(default=None, foreign_key="interactions.id")
    interaction: Optional["Interaction"] = Relationship(back_populates="messages")
