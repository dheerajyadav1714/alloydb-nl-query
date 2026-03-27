import os
import re
import logging
import psycopg2
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from google import genai

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

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
        model="gemini-2.5-flash",   # you can also use gemini-2.0-flash
        contents=prompt
    )
    sql_text = response.text.strip()
    # Remove markdown code fences if present
    sql_text = re.sub(r'^```sql\n', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'\n```$', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'^```\n', '', sql_text)
    sql_text = re.sub(r'\n```$', '', sql_text)
    return sql_text

def run_query(sql):
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>AlloyDB NL Query</title></head>
<body>
    <h1>Natural Language Query for Build Logs</h1>
    <form method="post">
        <label>Ask a question:</label><br>
        <input type="text" name="question" size="80" value="{{ question }}">
        <input type="submit" value="Submit">
    </form>
    {% if sql %}
        <h3>Generated SQL:</h3>
        <pre>{{ sql }}</pre>
    {% endif %}
    {% if results %}
        <h3>Results:</h3>
        <table border="1">
            <tr>
                <th>build_id</th><th>project_name</th><th>status</th><th>start_time</th><th>error_message</th>
            </tr>
            {% for row in results %}
            <tr>
                <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td>
            </tr>
            {% endfor %}
        </table>
    {% endif %}
    {% if error %}
        <p style="color:red">Error: {{ error }}</p>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    question = sql = results = error = None
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        logging.info(f"Received question: {question}")
        if question:
            try:
                logging.info("Generating SQL...")
                sql = generate_sql(question)
                logging.info(f"Generated SQL: {sql}")
                logging.info("Running query...")
                results = run_query(sql)
                logging.info(f"Results: {len(results)} rows")
            except Exception as e:
                error = str(e)
                logging.error(f"Error: {error}")
    return render_template_string(HTML_TEMPLATE, question=question, sql=sql, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
