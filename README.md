```markdown
# Natural Language Query Interface for CI/CD Build Logs with AlloyDB AI

## Use Case
Query CI/CD pipeline build logs using natural language, powered by AlloyDB and Gemini.

## Features
- Custom `builds` table with realistic build data
- Convert plain English questions to SQL using Gemini 2.5 Flash
- Execute SQL against AlloyDB and display results

## Prerequisites
- Google Cloud project with AlloyDB cluster and instance
- AlloyDB AI extensions enabled (`google_ml_integration`, `vector`)
- Gemini API key (from Google AI Studio)
- Python 3.9+ with `pip`

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/dheerajyadav1714/alloydb-nl-query.git
cd alloydb-nl-query
```

### 2. Install Dependencies
```bash
pip install google-genai psycopg2-binary python-dotenv
```

### 3. Set Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=your_alloydb_public_ip
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=alloydb
```

### 4. Load Sample Data
```bash
python3 load_data.py
```

### 5. Run the Natural Language Interface
```bash
python3 nl_to_sql.py
```
Enter your question, e.g., *"Show me all builds with status FAILURE"*.

## Example Queries
- `Show me all builds with status FAILURE`
- `What is the average duration of successful builds?`
- `Find builds triggered by alice`
- `List builds with error message containing 'timeout'`

## How It Works
1. User asks a question in natural language.
2. Gemini translates it to SQL using the table schema.
3. SQL is executed against AlloyDB.
4. Results are printed.

## Security Note
The `.env` file contains secrets – never commit it. The AlloyDB public IP should be restricted to trusted IPs.

## License
MIT
