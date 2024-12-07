import boto3
from botocore.exceptions import ClientError
from app.config import Config

def cleanup_resources():
    # Initialize AWS clients
    dynamodb = boto3.client('dynamodb',
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_KEY
    )
    
    s3 = boto3.client('s3',
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_KEY
    )

    # Delete DynamoDB tables
    tables_to_delete = [Config.EMPLOYEE_TABLE, Config.LEAVE_TABLE]
    
    for table_name in tables_to_delete:
        try:
            print(f"Deleting DynamoDB table: {table_name}")
            dynamodb.delete_table(TableName=table_name)
            waiter = dynamodb.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
            print(f"Successfully deleted table: {table_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Table {table_name} does not exist")
            else:
                print(f"Error deleting table {table_name}: {str(e)}")

    # Delete S3 bucket
    try:
        # First, delete all objects in the bucket
        print(f"Deleting all objects in bucket: {Config.S3_BUCKET}")
        bucket = boto3.resource('s3').Bucket(Config.S3_BUCKET)
        bucket.objects.all().delete()
        
        # Then delete the bucket
        print(f"Deleting S3 bucket: {Config.S3_BUCKET}")
        s3.delete_bucket(Bucket=Config.S3_BUCKET)
        print(f"Successfully deleted bucket: {Config.S3_BUCKET}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Bucket {Config.S3_BUCKET} does not exist")
        else:
            print(f"Error deleting bucket {Config.S3_BUCKET}: {str(e)}")

if __name__ == "__main__":
    print("Starting cleanup of AWS resources...")
    cleanup_resources()
    print("Cleanup completed!")