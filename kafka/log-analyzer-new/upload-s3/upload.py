import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

"""Uploads a list of local files to an Amazon S3 bucket."""
def upload_files_to_s3(bucket_name, file_paths):
    # Initialize the S3 client
    s3_client = boto3.client('s3')
    
    for file_path in file_paths:
        # Extract the file name from the local path to use as the S3 object key
        object_name = os.path.basename(file_path)
        
        try:
            print(f"Uploading {object_name}...")
            s3_client.upload_file(file_path, bucket_name, object_name)
            print(f"Successfully uploaded {object_name} to {bucket_name}")
        except ClientError as e:
            print(f"Failed to upload {object_name}: {e}")
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")

if __name__ == "__main__":
    BUCKET_NAME = "examens-arbete"
    
    files_to_upload = [
        r"C:\Users\metet\Desktop\aws-version\kafka\log-analyzer-new\log_report_kafka.csv",
        r"C:\Users\metet\Desktop\aws-version\kafka\log-analyzer-new\report-kafka.png"
    ]
    
    upload_files_to_s3(BUCKET_NAME, files_to_upload)