import logging
from celery import Celery
from celery.exceptions import Retry
import time
import os
import json
from dotenv import load_dotenv
from kafka_producer import send_event

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_BROKER_URL = os.getenv("RABBITMQ_BROKER_URL", "pyamqp://guest:guest@localhost:5672/")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "rpc://")

logger.info(f"Broker URL: {RABBITMQ_BROKER_URL}")
logger.info(f"Result Backend: {RESULT_BACKEND}")

celery_app = Celery(
    "celery_worker",
    broker=RABBITMQ_BROKER_URL,
    backend=RESULT_BACKEND
)

celery_app.conf.broker_connection_retry_on_startup = True

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, name="celery_worker.process_job")
def process_job(self, job_data):
    try:
        logger.info(f"Processing job: {job_data['job_id']}")

        # Send Kafka event

        send_event("job-events", {
            "event": "job_started",
            "job_id": job_data["job_id"],
            "title": job_data["title"],
            "status": "started"
        })

        # Simulating job processing
        time.sleep(5)

        # kafka event:job completed

        send_event("job-events", {
            "event": "job_completed",
            "job_id": job_data["job_id"],
            "title": job_data["title"],
            "status": "completed"
        })

        logger.info(f"Completed job: {job_data['job_id']}")
        return {
            "status": "completed",
            "job_id": job_data["job_id"],
            "title": job_data["title"]
        }
    except Exception as e:
        logger.error(f"Error processing job {job_data['job_id']}: {str(e)} - Retrying...")
        self.retry(exc=e)
