from fastapi import FastAPI, HTTPException
import os
import json
from pydantic import BaseModel
from typing import Optional, Literal
from uuid import uuid4
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Job model
class Job(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    job_id: Optional[str] = uuid4().hex  # UUID will be assigned automatically

JOBS_FILE = "jobs.json"
JOB_DATABASE = []


if os.path.exists(JOBS_FILE):
    with open(JOBS_FILE, "r") as f:
        JOB_DATABASE = json.load(f)

#/home
@app.get("/")
async def home():
    return {"Message": "Welcome to the Job Submission API"}

#/list-jobs
@app.get("/list-jobs")
async def list_jobs():
    return {"jobs": JOB_DATABASE}

#/job-by-index
@app.get("/job-by-index/{index}")
async def job_by_index(index: int):
    if not JOB_DATABASE:
        raise HTTPException(404, "No jobs available")
    if index < 0 or index >= len(JOB_DATABASE):
        raise HTTPException(404, f"Index {index} is out of range. Total jobs: {len(JOB_DATABASE)}")
    return {"job": JOB_DATABASE[index]}

#/submit-job
@app.post("/submit-job")
async def submit_job(job: Job):
    job.job_id = uuid4().hex  
    json_job = jsonable_encoder(job)  
    JOB_DATABASE.append(json_job)
    with open(JOBS_FILE, "w") as f:
        json.dump(JOB_DATABASE, f, indent=4)
    return {"Message": f"Job '{job.title}' was submitted.", "job_id": job.job_id}

#/get-job
@app.get("/get-job/{job_id}")
async def get_job(job_id: str):
    for job in JOB_DATABASE:
        if job["job_id"] == job_id: 
            return job
    raise HTTPException(404, f"Job not found: {job_id}")
