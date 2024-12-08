import boto3
from botocore.exceptions import ClientError
from app.config import Config
import time

def cleanup_resources():
    print("\n🧹 Starting cleanup of AWS resources...")
    
    try:
        # Use default credentials from AWS CLI configuration
        session = boto3.Session(region_name='ap-south-1')
        dynamodb = session.client('dynamodb')
        s3 = session.client('s3')
        
        print("\n📊 Cleaning DynamoDB tables...")
        tables_to_delete = [
            Config.EMPLOYEE_TABLE,
            Config.LEAVE_TABLE,
            Config.USER_TABLE
        ]
        
        for table_name in tables_to_delete:
            try:
                print(f"  ⌛ Deleting table: {table_name}")
                dynamodb.delete_table(TableName=table_name)
                waiter = dynamodb.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name)
                print(f"  ✅ Successfully deleted table: {table_name}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"  ℹ️ Table {table_name} does not exist")
                else:
                    print(f"  ❌ Error deleting table {table_name}: {str(e)}")

        # List all buckets and find HRMS-related ones
        print("\n📦 Cleaning S3 buckets...")
        response = s3.list_buckets()
        hrms_buckets = [bucket['Name'] for bucket in response['Buckets'] 
                       if bucket['Name'].startswith('f13-hrms-documents')]
        
        print(f"  Found {len(hrms_buckets)} HRMS-related buckets")
        
        for bucket_name in hrms_buckets:
            try:
                print(f"\n  🗑️ Processing bucket: {bucket_name}")
                
                # Delete all objects
                paginator = s3.get_paginator('list_objects_v2')
                
                try:
                    object_count = 0
                    for page in paginator.paginate(Bucket=bucket_name):
                        if 'Contents' in page:
                            objects = page['Contents']
                            object_count += len(objects)
                            
                            # Delete objects in batches
                            if objects:
                                s3.delete_objects(
                                    Bucket=bucket_name,
                                    Delete={
                                        'Objects': [{'Key': obj['Key']} for obj in objects]
                                    }
                                )
                    
                    print(f"    ✅ Deleted {object_count} objects")
                    
                    # Delete bucket
                    s3.delete_bucket(Bucket=bucket_name)
                    print(f"    ✅ Successfully deleted bucket: {bucket_name}")
                    
                except ClientError as e:
                    print(f"    ❌ Error processing bucket {bucket_name}: {str(e)}")
                    
            except ClientError as e:
                print(f"    ❌ Error accessing bucket {bucket_name}: {str(e)}")
                
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("1. Check AWS credentials configuration")
        print("2. Verify IAM permissions")
        print("3. Check network connectivity")
        return

    print("\n✨ Cleanup process completed!")

if __name__ == "__main__":
    cleanup_resources()
