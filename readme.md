# install
pip install google.cloud.storage
https://cloud.google.com/sdk/docs/install?hl=fr
## auth google
gcloud auth application-default login
## create gcloud project
gcloud projects create "uniqueID"
setup the billing on your project https://console.cloud.google.com/billing/projects

# create and delete s3
python create-google-s3-and-put-docs.py --bucket_name gr12-qs-3 --local_path pdf
to delete, modify the bucket name in delete-google-s3.py with the name of your bucket