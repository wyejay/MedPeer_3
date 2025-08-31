# Storage adapter: local fallback or S3 using boto3
import os
import boto3
from botocore.exceptions import ClientError
from flask import current_app
from werkzeug.utils import secure_filename

def upload_file_to_s3(file_obj, filename=None):
    # filename: original filename or custom
    filename = filename or secure_filename(file_obj.filename)
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    if not bucket or not os.environ.get('AWS_ACCESS_KEY_ID'):
        # Local fallback
        upload_folder = current_app.config.get('LOCAL_UPLOAD_FOLDER','uploads')
        os.makedirs(upload_folder, exist_ok=True)
        dest = os.path.join(upload_folder, filename)
        file_obj.save(dest)
        return {'storage_key': dest, 'url': dest, 'provider':'local'}
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                      region_name=region)
    key = f"uploads/{filename}"
    try:
        s3.upload_fileobj(file_obj, bucket, key, ExtraArgs={'ACL':'private'})
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        return {'storage_key': key, 'url': url, 'provider':'s3'}
    except ClientError as e:
        current_app.logger.error('S3 upload failed: %s', e)
        raise
