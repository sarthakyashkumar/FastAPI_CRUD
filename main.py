from contextlib import asynccontextmanager
# from random import randint
from fastapi import FastAPI, Depends,HTTPException
from datetime import datetime,timezone
from typing import Any,Annotated, Generic, TypeVar


#From here we are going to add the database with the sql so that we can fetch new tyoe of data.
from pydantic import BaseModel
from sqlmodel import create_engine,SQLModel,Session,Field,select

class Campaign(SQLModel,table=True):
    campaign_id:int | None=Field(default=None,primary_key=True)
    name:str=Field(index=True)
    due_date:datetime|None=Field(default=None,index=True)
    created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc),nullable=True,index=True)

class CampaignCreate(SQLModel):
    name:str
    due_date:datetime|None=None


sqlite_file_name="database.db"
sqlite_url=f"sqlite:///{sqlite_file_name}"
connect_args={"check_same_thread":False}
engine=create_engine(sqlite_url,connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_sessions():
    with Session(engine) as session:
        campaigns = session.exec(select(Campaign)).all()
        if not campaigns:
            session.add_all([
                Campaign(name="Summer Launch",due_date=datetime.now()),
                Campaign(name="Black Friday", due_date=datetime.now())
            ])
        yield session

SessionDep=Annotated[Session,Depends(get_sessions)]

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield



app=FastAPI(root_path="/api/v1",lifespan=lifespan)    #we have given default root path that would be applied to all the decorators mentioned below

#now to understand better we are going to create a dictionary which might replicate data from a database. It will be an array which contains dictionary of data about the different campaigns.
data:Any=[
    {"campaign_id":1,
     "name":"Summer Launch",
     "due_date":datetime.now(),
     "created_at":datetime.now()},
     {
    "campaign_id":2,
     "name":"Black Friday",
     "due_date":datetime.now(),
     "created_at":datetime.now()}
]


@app.get("/")
async def root():
    return {"message":"Hello world"}

T=TypeVar("T")
class Response(BaseModel,Generic[T]):
    data:T


@app.get("/campaigns",response_model=Response[list[Campaign]])
async def read_campaigns(session:SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data":data}

# @app.get("/campaigns")  #To get all the campaigns  
# def read_campaigns():
#     return {"campaign":data}

@app.get("/campaigns/{id}",response_model=Response[Campaign])
async def get_single_data(id:int,session:SessionDep):
    data=session.get(Campaign,id)
    if not data:
        return HTTPException(status_code=404)
    return {"data":data}

# @app.get("/campaigns/{id}")   #To get a particular campaign
# async def read_single_campaign(id:int):
#     for campaign in data:
#         if campaign.get("campaign_id")==id:
#             return {"campaign":campaign}
#     raise HTTPException(status_code=404)


@app.post("/campaigns",response_model=Response[Campaign],status_code=201)
async def create_campaign(campaign:CampaignCreate,session:SessionDep):
    db_campaign=Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data":db_campaign}

# """Now to post a new data via the docs page we are going to use somewhat this type of code"""
# @app.post("/campaigns")
# async def put_new_data(body:dict[str,Any]):

#     new : Any={
#         "campaign_id":randint(100,1000),
#         "name":body.get("name"),
#         "due_date":body.get("due_date"),
#         "created_at":datetime.now()
#     }
#     data.append(new)
#     return {"campaign":new}

@app.put("/campaigns/{id}",response_model=Response[Campaign])
async def update_campaigns(id:int,session:SessionDep,campaign:CampaignCreate):
    data=session.get(Campaign,id)
    if not data:
        return HTTPException(status_code=404)
    data.name=campaign.name
    data.due_date=campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}

# @app.put("/campaigns/{id}")
# async def update_data(id:int,body:dict[str,Any]):
#     for index,campaign in enumerate(data):
#         if campaign.get("campaign_id")==id:
#             updated: Any={
#                 "campaign_id":id,
#                 "name":body.get("name"),
#                 "due_date":campaign.get("due_date"),
#                 "created_at":campaign.get("created_at")
#             }
#             return {"campaign":updated}
#             data[index]=updated
#     raise HTTPException(status_code=404)


@app.delete("/campaigns/{id}",status_code=204)
async def delete_campaign(id:int,session:SessionDep):
    data=session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()

'''
Campaigns:
- campaign_id
- name
- due_date
- created_at
'''
