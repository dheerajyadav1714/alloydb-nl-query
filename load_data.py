import os
import psycopg2
import random
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# Sample data
projects = ["web-app", "api-service", "data-pipeline", "mobile-backend", "infra-tool"]
statuses = ["SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"]
error_messages = [
    "npm install failed: ENOENT",
    "timeout after 10 minutes",
    "no space left on device",
    "connection refused",
    "invalid credentials",
    "build script exited with code 1",
    None
]
users = ["alice", "bob", "ci-bot", "jenkins", "github-actions"]
branches = ["main", "develop", "feature/logging", "hotfix/critical"]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Generate 200 rows
for _ in range(200):
    project = random.choice(projects)
    status = random.choice(statuses)
    start = random_date(datetime(2025, 3, 1), datetime(2025, 3, 27))
    duration = random.randint(30, 1800)  # seconds
    end = start + timedelta(seconds=duration)
    error = random.choice(error_messages) if status != "SUCCESS" else None
    triggered_by = random.choice(users)
    branch = random.choice(branches)
    commit = uuid.uuid4().hex[:8]

    cur.execute("""
        INSERT INTO builds (project_name, status, start_time, end_time, duration_seconds, error_message, triggered_by, source_branch, commit_sha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (project, status, start, end, duration, error, triggered_by, branch, commit))

conn.commit()
cur.close()
conn.close()
print("Data inserted successfully!")
