# Job Submission API with Celery and Kafka

## Overview
This project is a **FastAPI-based Job Submission API** that supports **asynchronous job processing** using **Celery with RabbitMQ** as a task queue and **Kafka** for event-driven job tracking.

## Features
- **FastAPI** for job submission and management.
- **Celery** with RabbitMQ to handle job processing asynchronously.
- **Kafka** for event-driven job updates.
- **Dockerized** services for easy deployment.
- **Task tracking** using Celery’s result backend.
- **Thread-safe job database handling**.

## Project Structure
```
├── main.py                # FastAPI application
├── celery_worker.py       # Celery worker setup
├── kafka_producer.py      # Kafka producer for event streaming
├── kafka_consumer.py      # Kafka consumer for event monitoring
├── docker-compose.yml     # Docker Compose setup for RabbitMQ & Kafka
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
└── README.md              # Project documentation
```

## Installation & Setup
### Prerequisites
Make sure you have:
- **Python 3.8+**
- **Docker & Docker Compose**
- **RabbitMQ & Kafka**

### Step 1: Clone the Repository
```sh
git clone https://github.com/Kunal-AI-git/fastapi-job-api
cd your-repo
```

### Step 2: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 3: Start RabbitMQ & Kafka Using Docker
```sh
docker-compose up -d
```

### Step 4: Start Celery Worker
```sh
python -m celery -A celery_worker worker --loglevel=info --pool=solo
```

### Step 5: Run FastAPI Server
```sh
python -m uvicorn main:app --reload
```

### Step 6: Run Kafka Consumer
```sh
python kafka_consumer.py
```

## API Endpoints
### 1️⃣ Home Route
**GET /**
#### Response:
```json
{
  "Message": "Welcome to the Job Submission API"
}
```

### 2️⃣ Submit a Job
**POST /submit-job**
#### Request Body:
```json
{
  "title": "Data Processing Task",
  "description": "Process dataset XYZ",
  "priority": "high"
}
```
#### Response:
```json
{
  "Message": "Job 'Data Processing Task' was submitted.",
  "job_id": "a1b2c3d4",
  "task_id": "xyz123"
}
```

### 3️⃣ Check Task Status
**GET /get-task-status/{task_id}**
#### Response:
```json
{
  "task_id": "xyz123",
  "status": "SUCCESS",
  "result": {
    "status": "completed",
    "job_id": "a1b2c3d4",
    "title": "Data Processing Task"
  }
}
```

## Celery Task Workflow
1. **Job Submitted** → Sent to Celery queue via RabbitMQ.
2. **Worker Processes Job** → Celery worker picks up the task.
3. **Job Completion** → Celery updates the status and sends a Kafka event.

## Kafka Event-Driven Workflow
1. **Job Submitted** → Kafka event: `job_submitted`
2. **Job Started** → Kafka event: `job_started`
3. **Job Completed** → Kafka event: `job_completed`

## Monitoring
- **RabbitMQ Management UI**: `http://localhost:15672/` (user: guest, password: guest)
- **Kafka Consumer Output**: Logs job status updates in real-time

## Contributing
Feel free to submit **issues** and **pull requests**!

## License
MIT License

