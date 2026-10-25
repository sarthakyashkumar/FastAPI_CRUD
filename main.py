from random import randint

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Any
app=FastAPI(root_path="/api/v1")    #we have given default root path that would be applied to all the decorators mentioned below

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

@app.get("/campaigns")  #To get all the campaigns  
def read_campaigns():
    return {"campaign":data}


@app.get("/campaigns/{id}")   #To get a particular campaign
async def read_single_campaign(id:int):
    for campaign in data:
        if campaign.get("campaign_id")==id:
            return {"campaign":campaign}
    raise HTTPException(status_code=404)



"""Now to post a new data via the docs page we are going to use somewhat this type of code"""
@app.post("/campaigns")
async def put_new_data(body:dict[str,Any]):

    new : Any={
        "campaign_id":randint(100,1000),
        "name":body.get("name"),
        "due_date":body.get("due_date"),
        "created_at":datetime.now()
    }
    data.append(new)
    return {"campaign":new}


@app.put("/campaigns/{id}")
async def update_data(id:int,body:dict[str,Any]):
    for index,campaign in enumerate(data):
        if campaign.get("campaign_id")==id:
            updated: Any={
                "campaign_id":id,
                "name":body.get("name"),
                "due_date":campaign.get("due_date"),
                "created_at":campaign.get("created_at")
            }
            return {"campaign":updated}
            data[index]=updated
    raise HTTPException(status_code=404)




'''
Campaigns:
- campaign_id
- name
- due_date
- created_at
'''
