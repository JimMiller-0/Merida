# Merida
LLM Application Security Service (LASS)

Run Local - for Dev

1. pip install -r requirements.txt
2. export PROJECT_ID=<project_id>
3. export LOCATION=us-central1
3. export INSTANCE_HOST=127.0.0.1
5. export DB_USER=merida
6. export DB_PASS=<password2>
7. export DB_NAME=merida-db
8. export DB_PORT=5432
5. export INSTANCE_URI=<instance uri from last command>
4. flask run

Dev DB set up:

maunally create alloydb (in prod use jason TF)

create VM instance
install alloydb-auth-proxy #more info here: https://cloud.google.com/alloydb/docs/auth-proxy/connect#install
gcloud alloydb instances list
run alloydb-authproxy:
./alloydb-auth-proxy INSTANCE_URI

example: ./alloydb-auth-proxy \
  "projects/myproject/locations/us-central1/clusters/mycluster/instances/myprimary"

On local machine run:
gcloud compute ssh instance-1 --tunnel-through-iap --ssh-flag="-L 5432:localhost:5432"

Create DB:
gcloud alloydb users set-password postgres cluster=merida-dev --region=us-central1 --password=<password> 
gcloud alloydb users set-superuser postgres --superuser=true --cluster=merida-dev --region=us-central1
psql -h 127.0.0.1 -p 5432 -U postgres
<password>
CREATE DATABASE meridadb;
CREATE USER merida WITH PASSWORD ‘<password2>’;
GRANT ALL PRIVILEGES ON DATABASE meridadb TO merida;
gcloud alloydb users set-superuser merida --superuser=true --cluster=merida-dev --region=us-central1


Run in GCP - for Prod
