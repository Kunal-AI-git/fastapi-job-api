from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'job-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='job-monitor',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening for job events...")
for message in consumer:
    event = message.value
    print(f"Event: {event['event']} | Job ID: {event['job_id']} | Status: {event['status']}")
