import requests
import json
import os
from fastapi import FastAPI, Form, File, UploadFile
from bson import ObjectId
from fastapi import APIRouter, Request
from pymongo import MongoClient
import asyncio
from agents.meetingAgent import invokeAgents, transcriptGenerator
from moviepy.editor import VideoFileClip
router = APIRouter()
client = MongoClient("mongodb://localhost:27017/")
db = client["echoai"]
UPLOAD_FOLDER = "uploads"
import whisper
from nanoid import generate as generate_id
# model = whisper.load_model("small", "cpu")
@router.get("/crud-agent")
def crudAgent_endpoint():
    return {"message": "Hello from Crud Agent, Okay I'm not really an agent"}


@router.post("/create-meeting")
async def create_meeting(file: UploadFile = File(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    file_name = os.path.join("uploads", f"uploaded_{file.filename}")
    with open(file_name, "wb") as f:
        f.write(await file.read())
    video_clip = VideoFileClip(file_name)
    duration = video_clip.duration
    audio_clip = video_clip.audio
    audio_clip.write_audiofile("uploads/"+file.filename.split(".")[0]+".mp3")
    audio_clip.close()
    video_clip.close()
    new_meeting = db.meetings.insert_one({"video": file_name, "meetingDuration": duration})
    print(new_meeting.inserted_id)
    meetingid = str(new_meeting.inserted_id)
    asyncio.create_task(invokeAgents(meetingid, file.filename.split(".")[0]+".mp3"))
    return {"message": "meeting created", "meeting_id": str(new_meeting.inserted_id)}


@router.get("/get-meeting/{meeting_id}")
async def get_meeting(meeting_id: str):
    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    meeting["_id"] = str(meeting["_id"])
    suggestions = [meeting["agent"]["references"], meeting["agent"]["emails"]]
    m = {
        "meetingTranscript" : meeting["agent"]["transcript"],
        "meeting_id" : str(meeting["_id"]),
        "meetingTitle" : meeting["meetingName"],
        "meetingDuration" : meeting["meetingDuration"],
        "meetingAgenda" : meeting["agent"]["summary"],
        "suggestions": suggestions,
        "keytakeaways": meeting["agent"]["keyTakeways"],
        "absentia": meeting["agent"]["absentia"],
        "meetingFile": meeting["video"],
        "todo": meeting["agent"]["todo"]
    }
    
    return {"message": "successful", "meeting": m}


@router.get("/get-all")
async def get_all_meetings():
    meetings = db.meetings.find({})
    final = []
    for meeting in meetings:
        meeting["_id"] = str(meeting["_id"])
        final.append(meeting)
    return {"message": "successful", "meetings": final}

@router.get("/create-meeting")
async def create_meetings():
    meetingid = "1"
    asyncio.create_task(invokeAgents(meetingid, ""))



