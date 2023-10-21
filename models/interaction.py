from typing import List, Optional

from sqlmodel import Relationship, SQLModel

from .message import Message
from models.base import BaseModel


from models.base import BaseModel, Role


class Interaction(BaseModel, table=True):
    __tablename__ = "interactions"
    messages: Optional[List[Message]] = Relationship(back_populates="interaction")
    model_name: str = "gpt-3.5"
    role: Role = Role.SYSTEM.value
    prompt: Optional[str]