import os
import re
import psycopg2
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

def generate_sql(question):
    prompt = f"""You are an AI assistant that converts natural language questions into valid PostgreSQL SQL queries.
The database contains a table named "builds" with the following columns:
- build_id (UUID)
- project_name (TEXT)
- status (TEXT, values: SUCCESS, FAILURE, TIMEOUT, CANCELLED)
- start_time (TIMESTAMP)
- end_time (TIMESTAMP)
- duration_seconds (INTEGER)
- error_message (TEXT)
- triggered_by (TEXT)
- source_branch (TEXT)
- commit_sha (TEXT)
- cloud_build_id (TEXT)
- created_at (TIMESTAMP)

Only return the SQL query, no explanation, no markdown, no backticks.

Natural language: {question}
SQL:"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",   # change if needed
        contents=prompt
    )
    sql_text = response.text.strip()
    # Remove markdown code blocks if present
    sql_text = re.sub(r'^```sql\n', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'\n```$', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'^```\n', '', sql_text)
    sql_text = re.sub(r'\n```$', '', sql_text)
    return sql_text

def run_query(sql):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    question = input("Enter your natural language question: ")
    print("\nGenerating SQL...")
    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}\n")
    print("Running query...")
    results = run_query(sql)
    print("\nResults:")
    for row in results:
        print(row)
