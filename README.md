```markdown
# Natural Language Query Interface for CI/CD Build Logs with AlloyDB AI

## Use Case
Query CI/CD pipeline build logs using natural language, powered by AlloyDB and Gemini.

## Features
- Custom `builds` table with realistic build data
- Convert plain English questions to SQL using Gemini 2.5 Flash
- Execute SQL against AlloyDB and display results in a web interface
- Deployed on Cloud Run with VPC egress to AlloyDB private IP

## Prerequisites
- Google Cloud project with AlloyDB cluster and instance
- AlloyDB AI extensions enabled (`google_ml_integration`, `vector`)
- Gemini API key (from Google AI Studio)
- Python 3.9+ with `pip`

AlloyDB Setup
1. Enable Required Extensions
Connect to your AlloyDB instance (via psql or AlloyDB Studio) and run:

sql
CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;
2. Register the Gemini Model
Replace <<YOUR_PROJECT_ID>> with your GCP project ID:

sql
CALL google_ml.create_model(
   model_id => 'gemini-2.5-flash',
   model_request_url => 'https://aiplatform.googleapis.com/v1/projects/<<YOUR_PROJECT_ID>>/locations/global/publishers/google/models/gemini-2.5-flash:generateContent',
   model_qualified_name => 'gemini-2.5-flash',
   model_provider => 'google',
   model_type => 'llm',
   model_auth_type => 'alloydb_service_agent_iam'
);
3. Grant Vertex AI User Role to AlloyDB Service Account
Run this in Cloud Shell:

bash
PROJECT_ID=$(gcloud config get-value project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@gcp-sa-alloydb.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
4. Create the builds Table
sql
CREATE TABLE builds (
    build_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT,
    status TEXT CHECK (status IN ('SUCCESS', 'FAILURE', 'TIMEOUT', 'CANCELLED')),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    error_message TEXT,
    triggered_by TEXT,
    source_branch TEXT,
    commit_sha TEXT,
    cloud_build_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
5. Load Sample Data
Run the provided Python script load_data.py (which uses the environment variables in .env):

bash
python3 load_data.py
This will insert 200 synthetic build records.

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/dheerajyadav1714/alloydb-nl-query.git
   cd alloydb-nl-query
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables in a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   DB_HOST=your_alloydb_public_ip_or_private_ip
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=alloydb
   ```

4. Run the Flask app:
   ```bash
   python app.py
   ```

5. Open `http://localhost:8080` in your browser.

## Deployment to Cloud Run

The app is designed to run on Cloud Run with VPC egress to reach AlloyDB private IP.  
Use the following command (adjust subnet and network as needed):

```bash
gcloud beta run deploy alloydb-nl-query \
    --source . \
    --region us-central1 \
    --network easy-alloydb-vpc \
    --subnet easy-alloydb-subnet \
    --allow-unauthenticated \
    --vpc-egress=all-traffic \
    --set-env-vars "GEMINI_API_KEY=your_key,DB_HOST=10.182.0.2,DB_PORT=5432,DB_NAME=postgres,DB_USER=postgres,DB_PASSWORD=alloydb"
```

After deployment, grant the Cloud Run service account the `alloydb.client` role.

## Example Queries
- `Show me all builds with status FAILURE`
- `What is the average duration of successful builds?`
- `Find builds triggered by alice`
- `List builds with error message containing 'timeout'`

## How It Works
1. User asks a question in natural language.
2. Gemini translates it to SQL using the table schema.
3. SQL is executed against AlloyDB.
4. Results are displayed in a table.

<img width="1920" height="869" alt="image" src="https://github.com/user-attachments/assets/ea34ebac-530b-42ab-aa23-1dfaf6625f3f" />


## Security Note
- The `.env` file contains secrets – never commit it.
- For production, restrict AlloyDB access to private IP only and use a VPC connector.

## License
MIT
