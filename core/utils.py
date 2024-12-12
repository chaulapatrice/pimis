from datetime import datetime
import pytz
from django.conf import settings
import boto3
import os


def now() -> datetime:
    return datetime.now(tz=pytz.timezone(settings.TIME_ZONE))


access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')


def upload_file(file_name: str, key_name: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    bucket_name = 'pimis-ml'

    s3.upload_file(file_name, bucket_name, key_name)


def submit_batch_job():
    batch_client = boto3.client(
        'batch',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )

    job_name = 'pimis-predict-future-revenue'
    job_queue = 'BatchJobQueue1F419BDB-Qim7bzP0bu72fZJh'
    job_definition = 'BatchECSJobDefinitionA4-a815196f7773c8a:3'

    container_overrides = {
        'command': ['python', 'script.py'],
        'environment': [
            {'name': 'AWS_ACCESS_KEY_ID', 'value': access_key},
            {'name': 'AWS_SECRET_ACCESS_KEY', 'value': secret_key}
        ]
    }

    # Submit the job
    response = batch_client.submit_job(
        jobName=job_name,
        jobQueue=job_queue,
        jobDefinition=job_definition,
        containerOverrides=container_overrides
    )

    # Print the response
    print("Job submitted successfully!")
    print(f"Job ID: {response['jobId']}")
