from minio import Minio
from tempfile import NamedTemporaryFile
from datetime import timedelta

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


def list_documents_in_minio(bucket="protocols"):
    objects = client.list_objects(bucket, recursive=True)
    return [{"path": obj.object_name} for obj in objects]


def delete_from_minio(bucket, object_name):
    client.remove_object(bucket, object_name)


def generate_presigned_url(object_name: str, bucket: str = "protocols", expiry: int = 3600) -> str:
    try:
        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=expiry)  # ✅ THIS LINE
        )
        return url
    except Exception as e:
        print(e)
        raise RuntimeError(f"Failed to generate download URL: {e}")
