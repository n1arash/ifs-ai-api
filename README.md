
#### Project Tools:
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLModel
- G4F (Gpt 4 Free)


## Project Structure:

- 📁 db: contains session dependency and sqlmodel engine 
- 📁 models: contains all Models Definitions 
- 📁 routers: contains all project routers
- 📁 providers : G4F Provider Implementation

## Endpoints

```
GET /interactions/ -> return interaction with settings and messages
POST /interactions/ -> create interactions
GET /interactions/{uuid}/messages/ -> get messages for specific interaction
POST /interactions/{uuid}/messages/ -> create message for specific interaction
```

PS: go to the swagger docs at `/docs` path  for more detailed information about endpoints


## Project Database Schema

![Database Design](https://i.ibb.co/kmRFYXH/Pasted-image-20231021180408.png)

## Project Models

#### Ineteractions

Description:
We use interaction model to make custom user interaction to user be able to choose custom model and create system for the Chosen LLM model response
also there is a foreign key relationship between Interactions model and Messages model to enable us find specific messages for an interaction.

### Fields:
`-> : indicates field properties `
```
id: UUID 
created_at: timestamp -> default now
updated_at: timestamp -> default now | onupdate -> now
role: text -> default "System"
prompt: text -> default NULL // if this field specified while creating we will send every user input prompt with this field prompt as system  
```


#### Messages

Description:
we use Messages model as so we save user messages in the specific in interaction which is connected by a foreign key to the Interaction table id.
also we save AI responses in the database using this model too.
all of messages must have an `interaction_id` so we can identify this message is for which interaction.

### Fields:
```
id: UUID 
created_at: timestamp -> default now
updated_at: timestamp -> default now | onupdate -> now
role: text -> required
content: text -> required
interaction_id: UUID -> foreign key to interaction model id / required
```

NOTE:
we can use models to fetch relationship between fetched object for example:
```
m: Message = Message(role="Human", content="Hello AI", interaction_id=1-2-3-45)
# we can access interaction by calling below
interaction: Interaction = m.interaction.id # -> 1-2-3-45 
```
this works for interactions too by calling `interaction.messages` which will fetch all related messages to the interaction.

-----------------------
## Project Setup

before everything rename `.env.example` to `.env` and set `DATABASE_URL` 

### Easy Setup:
```
docker build -t ifs-ai-api .
docker run -it -p 8000:8000 ifs-ai-api

// or use docker-compose

docker compose build
docker compose up -d
```
after running project, it's accessible via `http://[ip|host|localhost]:8000`

### Manual/Dev Setup:

Requirements:
	- Python 3.12
	- Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 - #install poetry
poetry install # install dependencies
poetry shell # spawn into poetry shell
poetry run uvicorn main:app --reload # spawn uvicorn with autoreload
```

--------
## Run Tests

To run tests go into the root directory if you never ran project before you need to run it so `SQLModel` initiate the tables into the database then run command below:

```bash
pytest -vv
```

------


# Design Decisions

For this API, I have decided to use the Model-Controller Pattern, which is commonly used in API designs. There are two models in the project: Message and Interaction. These two models are related to each other, allowing us to fetch their data in both ways. This means that interactions know their messages and messages know their related interactions by using SQLAlchemy Relationships. This leads to a better developer experience and safer queries.
#### API Flow:
By adding an interaction, we prepare a provider and model for g4f, which requires this data to interact with mock LLM services and return LLM response to us. Then, by adding a message to the specific interaction, we schedule a FastAPI background task asynchronously to connect to the g4f provider. After receiving a response, we update the interaction by inserting an AI message with the AI role and message.


Ideas to Consider in future:

- Scalability: it's better we switch from FastAPI background tasks to a tool like Celery so we can have a fail safe approach to `G4F` service, also we might need to index columns like `interaction_id` in messages table to lower our query weight while fetching all interactions with messages. running several nodes of API application and using a LoadBalancer to distribute traffic to them also help. also this project is using SQLite as database we need to switch to a proper RDBMS database like PostgreSQL to get better performance and more database optimization options.
    
- Extensibility: Right now we can use all the supported `g4f` models and providers, but we may need to implement an abstract approach to contact 3rd party services like `g4f`.
    
- Security: of course we need an authentication approach like OAuth2 in this project to keep user interactions and messages safe. also we can implement end to end key exchange between client and server to enable us to encrypt user messages and interactions in the database. a 2FA authentication approach by SMS or Email also can help.
    
- Domain Segregation:
	- Clearly define and document the different domains or areas of functionality within our system. This will help us identify potential conflicts or inconsistencies between stored state and model actions.

	- Use a well-defined data model that accurately represents the entities and relationships within each domain. This will ensure that any changes to stored state are reflected in the model actions.

	- Implement proper validation and error handling mechanisms to prevent any invalid or conflicting changes to stored state.

	- Use versioning in our API to clearly distinguish between different versions of our data model and ensure backward compatibility.

	- Regularly review and update our implementation to ensure that it aligns with the defined domains and maintains consistency between stored state and model actions.
    PS: I didn't know much about this concept so i searched about it and these are what we can do for Domain Segregation in the project  
