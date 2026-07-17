# 1. Google Cloud CLI installieren:
# https://cloud.google.com/sdk/docs/install

# 2. Dieses Script ausfuehren:
#    deploy.bat

# 3. Oder manuell:
gcloud auth login
gcloud config set project vitalcoach-kevin
gcloud services enable run.googleapis.com firestore.googleapis.com cloudbuild.googleapis.com
gcloud firestore databases create --location=europe-west1

cd backend
gcloud builds submit --tag gcr.io/vitalcoach-kevin/vitalcoach
gcloud run deploy vitalcoach --image gcr.io/vitalcoach-kevin/vitalcoach --region europe-west1 --allow-unauthenticated --memory=512Mi

# Die URL wird angezeigt nach dem Deploy - z.B.:
# https://vitalcoach-xxxxxx-ew.a.run.app

# 4. Auf Handy oeffnen und zum Homescreen hinzufuegen!
