from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn
from agents.crudagent import router as crudAgent_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(crudAgent_router, prefix="/api", tags=["CRUD Agent"])
# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["mycollection"]


@app.get("/api")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
