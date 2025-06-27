from minio import Minio
from tempfile import NamedTemporaryFile

client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def upload_to_minio(bucket: str, filename: str, file_obj):
    client.put_object(
        bucket_name=bucket,
        object_name=filename,
        data=file_obj,
        length=file_obj.size,
        content_type="application/pdf"
    )

def download_from_minio(bucket: str, filename: str) -> str:
    response = client.get_object(bucket, filename)
    tmp = NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(response.read())
    tmp.close()
    return tmp.name
