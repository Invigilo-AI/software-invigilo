from uuid import uuid4
from datetime import datetime, timedelta
import boto3
import mimetypes

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings


class CRUDUpload:
    def __init__(self) -> None:
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY
        )
        self.bucket = settings.S3_BUCKET

    async def fetch_upload(self, object_key: str):
        try:
            s3_response = self.s3.get_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            if s3_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return StreamingResponse(content=s3_response['Body'].iter_chunks(), media_type=s3_response['ContentType'])
        except Exception as e:
            # TODO consider other exceptions
            print("ERROR:fetch_upload:", e)
        return None

    async def temporary_upload(self, file: UploadFile, prefix: str = 'temp'):
        filename = str(uuid4())

        try:
            object_key = f"{prefix}/{filename}"
            mime_type, _ = mimetypes.guess_type(file.filename)
            data = await file.read()
            s3_response = self.s3.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=data,
                ContentType=mime_type,
                Expires=datetime.utcnow() + timedelta(hours=1)
            )

            if s3_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                object_key = None
        except Exception as e:
            # TODO consider other exceptions
            print("ERROR:temporary_upload:", e)
            object_key = None
        return {
            "object_id": object_key,
            "object_url": self.sign_url(object_key)
        }

    async def remove_temporary_upload(self, object_key: str):
        try:
            s3_response = self.s3.delete_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            if s3_response["ResponseMetadata"]["HTTPStatusCode"] != 204:
                object_key = None
        except Exception as e:
            # TODO consider other exceptions
            print("ERROR:remove_temporary_upload:", e)
            object_key = None
        return {
            "object_id": object_key
        }

    async def move_temporary_upload(self, object_key: str, move_key: str):
        try:
            self.s3.copy(
                {
                    'Bucket': self.bucket,
                    'Key': object_key
                },
                self.bucket,
                move_key,
            )
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=object_key,
            )
        except Exception as e:
            # TODO consider other exceptions
            print("ERROR:move_temporary_upload:", e)
            return False
        return True

    def sign_url(self, object_key: str, expires_in: int = 3600):
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_key
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            # TODO consider other exceptions
            print("ERROR:sign_url:", e)
            return None


upload = CRUDUpload()
