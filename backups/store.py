import boto3

from .settings import AWS_PROFILE, BACKUP_S3_BUCKET

session = boto3.Session(profile_name=AWS_PROFILE)
s3_client = session.client('s3')


def list_s3_files():
    resp = s3_client.list_objects(Bucket=BACKUP_S3_BUCKET)
    return resp['Contents']


def upload_fileobj_to_s3(f, key):
    s3_client.upload_fileobj(f, BACKUP_S3_BUCKET, key)
