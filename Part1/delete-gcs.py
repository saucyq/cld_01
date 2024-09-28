from google.cloud import storage


bucket_name = "gr12-qs-3"

storage_client = storage.Client()
# Delete all blobs in the bucket
bucket = storage_client.get_bucket(bucket_name)
blobs = bucket.list_blobs()
for blob in blobs:
    blob.delete()
    print(f'Deleted blob: {blob.name}')
bucket.delete()
