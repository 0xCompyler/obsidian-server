import os

import ibm_boto3
from ibm_botocore.client import Config, ClientError
import secrets


BASE_DIR = os.getcwd()
DUMP_DIR = os.path.join(BASE_DIR, 'DUMP')



def create_bucket(bucket_name: str):
    if bucket_name == '':
        return {"error": "Bucket name cannot be empty"}

    try:
        cos = ibm_boto3.resource("s3",
            ibm_api_key_id=secrets.api_key,
            ibm_service_instance_id=secrets.instance_crn,
            config=Config(signature_version="oauth"),
            endpoint_url=secrets.endpoint
        )
    except:
        return {"error": "connection error"}

    try:
        cos.Bucket(bucket_name).create(
                    CreateBucketConfiguration={
                        "LocationConstraint":secrets.location
                    }
                )
        return {"status": "ok"}
    except Exception as e:
        return {"error": e}    


def list_files(bucket_name: str):
    cos = ibm_boto3.resource("s3",
            ibm_api_key_id=secrets.api_key,
            ibm_service_instance_id=secrets.instance_crn,
            config=Config(signature_version="oauth"),
            endpoint_url=secrets.endpoint
        )
    files = cos.Bucket(bucket_name).objects.all()




def upload_file(bucket_name: str, item_name: str, file_path: str):
    try:
        cos = ibm_boto3.resource("s3",
            ibm_api_key_id=secrets.api_key,
            ibm_service_instance_id=secrets.instance_crn,
            config=Config(signature_version="oauth"),
            endpoint_url=secrets.endpoint
        )
    except Exception as e:
        return {"error": e}  

    part_size = 1024 * 1024 * 5
    file_threshold = 1024 * 1024 * 15
    transfer_config = ibm_boto3.s3.transfer.TransferConfig(
        multipart_threshold=file_threshold,
        multipart_chunksize=part_size
    )

    with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

    return {"url": f"https://{bucket_name}.{secrets.endpoint[8: ]}/{item_name}"}


def download_files(bucket_name: str, item_name: str):
    cos = ibm_boto3.resource("s3",
            ibm_api_key_id=secrets.api_key,
            ibm_service_instance_id=secrets.instance_crn,
            config=Config(signature_version="oauth"),
            endpoint_url=secrets.endpoint
        )
    
    file = cos.Object(bucket_name, item_name).get()
    content = file['Body'].read()
    with open(os.path.join(DUMP_DIR, item_name), 'wb') as f:
        f.write(content)

