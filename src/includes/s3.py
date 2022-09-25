import boto3
from os import environ
from io import BytesIO
from botocore.config import Config
from botocore.exceptions import ClientError
from includes import log

AWS_ACCESS_KEY_ID = environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION_NAME = environ["AWS_REGION_NAME"]
AWS_BUCKET_NAME = environ["AWS_BUCKET_NAME"]


class AwsStorage:
    def __init__(self):
        self._s3_client = boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME,
            config=Config(s3={"addressing_style": "path"}),
        )
        if not self._root_bucket_exists():
            self._create_root_bucket()

    def _create_root_bucket(self):
        """Create root S3 bucket

        :return: True if bucket created, else False
        """

        # Create bucket
        try:
            location = {"LocationConstraint": AWS_REGION_NAME}
            self._s3_client.create_bucket(
                Bucket=AWS_BUCKET_NAME, CreateBucketConfiguration=location
            )
        except ClientError as e:
            log.error(e)
            return False
        return True

    def _root_bucket_exists(self):
        response = self._s3_client.list_buckets()

        for bucket in response["Buckets"]:
            if bucket["Name"] == AWS_BUCKET_NAME:
                return True
        return False

    def list_files(self):
        response = self._s3_client.list_objects(Bucket=AWS_BUCKET_NAME)
        if "Contents" in response:
            return response['Contents']
        else:
            return []

    def store_file(self, file_path, data):
        self._s3_client.upload_fileobj(Fileobj=BytesIO(data), Bucket=AWS_BUCKET_NAME, Key=file_path)
        return "s3://{}/{}".format(AWS_BUCKET_NAME, file_path)

