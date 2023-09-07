# Merida
LLM Application Security Service (LASS)

Run Local - for Dev

1. pip install -r requirements.txt
2. export PROJECT_ID=<project_id>
3. export LOCATION=us-central1
3. export INSTANCE_HOST=127.0.0.1
5. export DB_USER=postgres
6. export DB_PASS=<db password>
7. export DB_NAME=merida-db
8. export DB_PORT=5432
4. gcloud alloydb instances list
5. export INSTANCE_URI=<instance uri from last command>
6. nohup ./alloydb-auth-proxy $INSTANCE_URI
4. flask run


Run in GCP - for Prod
