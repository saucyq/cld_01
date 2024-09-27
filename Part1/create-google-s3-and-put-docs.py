# Creator: Abir Chebbi (abir.chebbi@hesge.ch)
# modify : Quentin Saucy

# installer le paquet google.cloud.storage
# install google cli
#create gcloud project
#change the billing project
import boto3
import os
import argparse

from google.cloud import storage
#python create-google-s3-and-put-docs.py --bucket_name gr12-qs-s3
def create_bucket(bucket_name):
    """Creates a new bucket."""
    # bucket_name = "your-new-bucket-name"

    storage_client = storage.Client()

    bucket = storage_client.create_bucket(bucket_name)

    print(f"Bucket {bucket.name} created")
    return bucket
# Function to write files to S3
def write_files(s3_client, directory, bucket):
    print("write")
    generation_match_precondition = 0
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):  # Check if the file is a PDF
            #file_path = os.path.join(directory, filename)
            print(f"Uploading {filename} to bucket {bucket}...")
            s3_client.upload_from_filename(directory+"/"+filename, if_generation_match=generation_match_precondition)

            print(f"{filename} uploaded successfully.")

def main(bucket_name, local_dir):
    s3_client =create_bucket( bucket_name)
    s3_client=s3_client.blob("qs_test")

    write_files(s3_client, local_dir, bucket_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload PDF files to an S3 bucket")
    parser.add_argument("--bucket_name", help="The name of the S3 bucket to which the files will be uploaded")
    parser.add_argument("--local_path", help="The name of the folder to put the pdf files")
    args = parser.parse_args()
    main(args.bucket_name, args.local_path)

