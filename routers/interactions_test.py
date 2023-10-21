from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

from models.base import Role
from .interactions import router
from models import Message, Interaction

app = FastAPI()

app.include_router(router)

client = TestClient(app)


@app.on_event("startup")
def init_db():
    DATABASE_URL = "sqlite:///"
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False},
    )

    SQLModel.metadata.create_all(engine)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_interactions():
    response = client.get("/interactions/")
    response_data = response.json()

    assert response.status_code == 200

    if len(response_data["data"]) > 0:
        for interaction in response_data["data"]:
            assert interaction["id"]
            assert interaction["settings"]["model_name"]
            assert interaction["settings"]["role"] == Role.SYSTEM.value
            assert interaction["messages"]
    else:
        assert response_data["data"] == []


def test_create_interactions():
    data = {"prompt": "You are an expert tester."}
    response = client.post("/interactions/", json=data)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["id"]
    assert response_data["created_at"]
    assert response_data["updated_at"]
    assert response_data["prompt"] == data["prompt"]
    assert response_data["role"] == Role.SYSTEM.value


def test_get_interaction_messages_invalid_path_param():
    id = 4124124124
    response = client.get(f"/interactions/{id}/messages/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


def test_get_interaction_messages_404():
    id: UUID = uuid4()
    response = client.get(f"/interactions/{id}/messages/")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Interaction not found"}


def test_get_interaction_messages():
    interaction_response = client.post("/interactions/", json={})
    assert interaction_response.status_code == 200
    interactions_data = interaction_response.json()
    interaction_id = interactions_data["id"]
    assert interaction_id
    response = client.get(f"/interactions/{interaction_id}/messages/")
    assert response.status_code == 200
    assert response.json() == []


def test_add_message_to_interaction():
    """
        NOTE: it waits until g4f response come from one of providers.
    """
    interaction_response = client.post("/interactions/", json={})
    assert interaction_response.status_code == 200
    interactions_data = interaction_response.json()
    interaction_id = interactions_data["id"]
    assert interaction_id
    data = {"role": Role.HUMAN.value, "content": "Hello, AI!"}
    response = client.post(f"/interactions/{interaction_id}/messages/", json=data)
    assert response.status_code == 200
    assert response.json()
    response_data = response.json()
    assert response_data["role"] == data["role"]
    assert response_data["content"] == data["content"]
    assert response_data["id"]
