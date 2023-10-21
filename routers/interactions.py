import datetime
from typing import List
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import SQLModel, Session

from models import Interaction, Message
from db import get_session, engine
from models.base import BaseModel, Role
from provider.g4f import G4F

router = APIRouter(prefix="/interactions", tags=["Interactions"])


class Settings(SQLModel):
    model_name: str
    role: Role
    prompt: str | None = ""


class InteractionRead(BaseModel):
    settings: Settings
    messages: List[Message]


class InteractionList(SQLModel):
    data: List[InteractionRead]


@router.get("/", response_model=InteractionList)
async def get_interactions(session: Session = Depends(get_session)):
    """
    get all interactions
    :return:
    """
    interactions_with_messages: List[Interaction] = (
        session.query(Interaction).join(Interaction.messages).all()
    )
    data = [
        InteractionRead(
            id=interaction.id,
            created_at=interaction.created_at,
            updated_at=interaction.updated_at,
            messages=interaction.messages,
            settings=Settings(
                model_name=interaction.model_name,
                role=interaction.role,
                prompt=interaction.prompt,
            ),
        )
        for interaction in interactions_with_messages
    ]

    return InteractionList(data=data)
    # print(interactions_with_messages)
    # return interactions_with_messages


@router.post("/", response_model=Interaction)
async def create_interaction(
    interaction_in: Interaction, session: Session = Depends(get_session)
):
    """
    create an interaction
    :return:
    """
    try:
        interaction = Interaction.from_orm(interaction_in)
        session.add(interaction)
        session.commit()
        session.refresh(interaction)

        return interaction
    except:
        session.rollback()


@router.get("/{id}/messages/", response_model=List[Message])
async def get_interaction_messages(id: UUID, session: Session = Depends(get_session)):
    """
    get an interaction messages
    :return:
    """
    if not session.get(Interaction, id):
        raise HTTPException(status_code=404, detail="Interaction not found")

    messages: List[Message] = (
        session.query(Message).where(Message.interaction_id == str(id)).all()
    )

    if not messages:
        return []
    
    return messages


@router.post("/{id}/messages/", response_model=Message)
async def create_message_for_interaction(
    message_in: Message,
    id: UUID,
    background_task: BackgroundTasks,
    session: Session = Depends(get_session),
):
    """
    create message for an interaction
    :return:
    """
    if not id:
        raise HTTPException(status_code=400, detail="id is not provided")

    try:
        message_in.interaction_id = id
        message = Message.from_orm(message_in)
        session.add(message)
        session.commit()
        session.refresh(message)

        # you change provider and llm model by providing `provider` and `model_name` parameters
        # if you want to use proxy just pass proxy parameter
        # g4f docs: https://github.com/xtekky/gpt4free#models
        g4f = G4F()
        system_prompt = message.interaction.prompt
        background_task.add_task(
            g4f.run_async,
            interaction_id=message.interaction_id,
            role=Role.HUMAN.value,
            content=message.content,
            system_prompt=system_prompt,
        )

        return message
    except Exception as e:
        session.rollback()
        raise e
