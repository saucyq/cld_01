# Creator: Abir Chebbi (abir.chebbi@hesge.ch)
# modify : Quentin Saucy
# modify : Jonas Flückiger

import os
import argparse
from google.cloud import storage


def create_bucket(bucket_name):
    """Creates a new bucket."""
    # bucket_name = "your-new-bucket-name"

    storage_client = storage.Client()

    bucket = storage_client.create_bucket(bucket_name)

    print(f"Bucket {bucket.name} created")
    return bucket


# Function to write files to bucket
def upload_pdf_files(bucket_name, source_folder):
    # Initialize the GCS client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket(bucket_name)

    # Loop through the files in the local folder
    for file_name in os.listdir(source_folder):
        if file_name.endswith(".pdf"):
            # Full local path of the file
            local_file_path = os.path.join(source_folder, file_name)

            # Upload the PDF file
            # Use the file name as the GCS object name
            blob = bucket.blob(file_name)
            blob.upload_from_filename(local_file_path)

            print(f"Uploaded {file_name} to bucket {bucket_name}.")


def main(bucket_name, local_dir):
    create_bucket(bucket_name)
    upload_pdf_files(bucket_name, local_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload PDF files to a GCS bucket")
    parser.add_argument(
        "--bucket_name", help="The name of the GCS bucket to which the files will be uploaded")
    parser.add_argument(
        "--local_path", help="The name of the folder where the pdf files are located")
    args = parser.parse_args()
    main(args.bucket_name, args.local_path)
