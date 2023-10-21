from typing import Callable
from uuid import UUID
import g4f
from sqlmodel import Session
from db import engine
from g4f.Provider import (
    ChatgptX,
    ChatgptDemo,
    GptGo,
    You,
    NoowAi,
    GPTalk,
    GptForLove,
    Phind,
    ChatBase,
    Cromicle,
)
from models.base import Role
from models import Message


class G4F:
    model_name = g4f.models.gpt_35_turbo
    provider = g4f.Provider.RetryProvider(
        [
            ChatgptX,
            ChatgptDemo,
            GptGo,
            You,
            NoowAi,
            GPTalk,
            GptForLove,
            Phind,
            ChatBase,
            Cromicle,
        ]
    )
    proxy = None

    def __init__(self, provider=None, model_name=None, proxy=None) -> None:
        if provider:
            self.provider = provider
        if model_name:
            self.model_name = model_name
        if proxy:
            self.proxy = proxy

    async def run_async(
        self,
        interaction_id: UUID,
        role: Role = Role.HUMAN.value,
        content: str = "",
        system_prompt: str = "",
    ):
        if not role or not content:
            raise ValueError("Role or Content for AI interaction is not provided")
        if not interaction_id:
            raise ValueError("Interaction id is not provided")
        try:
            response = await g4f.ChatCompletion.create_async(
                model=self.model_name,
                messages=[
                    {"role": Role.SYSTEM.value, "content": system_prompt},
                    {"role": role, "content": content},
                ],
                provider=self.provider,
                proxy=self.proxy,
            )
            if response and interaction_id:
                await self._add_ai_message_to_interaction(
                    interaction_id=interaction_id, role=Role.AI.value, content=response
                )
        except Exception as e:
            raise e

    async def _add_ai_message_to_interaction(
        self, interaction_id: UUID = None, role: Role = "", content: str = ""
    ):
        with Session(engine) as session:
            try:
                message = Message(
                    role=role, content=content, interaction_id=interaction_id
                )
                session.add(message)
                session.commit()
            except:
                session.rollback()
            finally:
                session.close()
