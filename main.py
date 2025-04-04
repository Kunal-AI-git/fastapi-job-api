from fastapi import FastAPI, HTTPException
import os
import json
from pydantic import BaseModel
from typing import Optional, Literal
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from celery_worker import celery_app, process_job
from dotenv import load_dotenv 
from threading import Lock
from kafka_producer import send_event

load_dotenv()

app = FastAPI()
file_lock=Lock()

# Job Model
class Job(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    job_id: Optional[str] = None

JOBS_FILE = os.getenv("JOBS_FILE", "jobs.json")
JOB_DATABASE = []

if os.path.exists(JOBS_FILE):
    with open(JOBS_FILE, "r") as f:
        try:
            JOB_DATABASE = json.load(f)
        except json.JSONDecodeError:
            JOB_DATABASE=[]    

@app.get("/")
async def home():
    return {"Message": "Welcome to the Job Submission API"}

@app.get("/list-jobs")
async def list_jobs():
    return {"jobs": JOB_DATABASE}

@app.post("/submit-job")
async def submit_job(job: Job):
    job.job_id = uuid4().hex  
    json_job = jsonable_encoder(job)

    try:
        # Send job to Celery queue
        task = celery_app.send_task("celery_worker.process_job", args=[json_job])

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to submit job to the queue.")

    with file_lock:
        JOB_DATABASE.append(json_job)
        with open(JOBS_FILE, "w") as f:
            json.dump(JOB_DATABASE, f, indent=4)

 #senf kafka event
 
    send_event("job-events", {
        "event": "job_submitted",
        "job_id": job.job_id,
        "title": job.title,
        "status": "submitted"
    })        

    return {
        "Message": f"Job '{job.title}' was submitted.",
        "job_id": job.job_id,
        "task_id": task.id
    }


@app.get("/get-task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)

    return {
    "task_id": task_id,
    "status": task_result.status,
    "result": task_result.result}
