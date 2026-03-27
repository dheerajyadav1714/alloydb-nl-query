```markdown
# Natural Language Query Interface for CI/CD Build Logs with AlloyDB AI

## Use Case
Query CI/CD pipeline build logs using natural language, powered by AlloyDB and Gemini.

## Live Demo
Visit the deployed application:  
[https://alloydb-nl-query-688623456290.us-central1.run.app/](https://alloydb-nl-query-688623456290.us-central1.run.app/)

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

## Security Note
- The `.env` file contains secrets – never commit it.
- For production, restrict AlloyDB access to private IP only and use a VPC connector.

## License
MIT
