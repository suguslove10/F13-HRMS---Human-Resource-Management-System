import boto3
from botocore.exceptions import ClientError
import bcrypt
import uuid
from datetime import datetime

def create_tables_and_bucket(app):
    dynamodb = boto3.resource('dynamodb',
        region_name=app.config['AWS_REGION'],
        aws_access_key_id=app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=app.config['AWS_SECRET_KEY']
    )

    # Create User table
    try:
        table = dynamodb.create_table(
            TableName=app.config['USER_TABLE'],
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {app.config['USER_TABLE']}...")
        table.wait_until_exists()

        # Create default admin user
        try:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), salt)
            
            table.put_item(Item={
                'userId': str(uuid.uuid4()),
                'email': 'admin@f13.com',
                'password': password_hash.decode('utf-8'),
                'role': 'ADMIN',
                'firstName': 'Admin',
                'lastName': 'User',
                'createdAt': datetime.now().isoformat()
            })
            print("Created default admin user")
        except ClientError as e:
            print(f"Admin user might already exist: {str(e)}")
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {app.config['USER_TABLE']} already exists")
        else:
            print(f"Error creating table: {str(e)}")

    # Create Employee table
    try:
        table = dynamodb.create_table(
            TableName=app.config['EMPLOYEE_TABLE'],
            KeySchema=[
                {'AttributeName': 'employeeId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'employeeId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {app.config['EMPLOYEE_TABLE']}...")
        table.wait_until_exists()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {app.config['EMPLOYEE_TABLE']} already exists")
        else:
            print(f"Error creating table {app.config['EMPLOYEE_TABLE']}: {str(e)}")

    # Create Leave table
    try:
        table = dynamodb.create_table(
            TableName=app.config['LEAVE_TABLE'],
            KeySchema=[
                {'AttributeName': 'leaveId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'leaveId', 'AttributeType': 'S'},
                {'AttributeName': 'employeeId', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmployeeIndex',
                    'KeySchema': [
                        {'AttributeName': 'employeeId', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {app.config['LEAVE_TABLE']}...")
        table.wait_until_exists()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {app.config['LEAVE_TABLE']} already exists")
        else:
            print(f"Error creating table {app.config['LEAVE_TABLE']}: {str(e)}")

    # Create S3 bucket
    s3 = boto3.client('s3',
        region_name=app.config['AWS_REGION'],
        aws_access_key_id=app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=app.config['AWS_SECRET_KEY']
    )

    try:
        if app.config['AWS_REGION'] == 'us-east-1':
            # For us-east-1, don't specify LocationConstraint
            s3.create_bucket(Bucket=app.config['S3_BUCKET'])
        else:
            # For other regions, specify LocationConstraint
            s3.create_bucket(
                Bucket=app.config['S3_BUCKET'],
                CreateBucketConfiguration={'LocationConstraint': app.config['AWS_REGION']}
            )
        print(f"Created S3 bucket: {app.config['S3_BUCKET']}")

        # Set bucket CORS policy
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': []
            }]
        }
        s3.put_bucket_cors(
            Bucket=app.config['S3_BUCKET'],
            CORSConfiguration=cors_configuration
        )
        
        # Set bucket public access block
        s3.put_public_access_block(
            Bucket=app.config['S3_BUCKET'],
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        
        print("Configured S3 bucket security settings")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {app.config['S3_BUCKET']} already exists")
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f"Bucket {app.config['S3_BUCKET']} already exists but is owned by another account")
            # Generate a unique bucket name by adding a timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_bucket_name = f"{app.config['S3_BUCKET']}-{timestamp}"
            app.config['S3_BUCKET'] = new_bucket_name
            
            if app.config['AWS_REGION'] == 'us-east-1':
                s3.create_bucket(Bucket=new_bucket_name)
            else:
                s3.create_bucket(
                    Bucket=new_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': app.config['AWS_REGION']}
                )
            print(f"Created S3 bucket with new name: {new_bucket_name}")
        else:
            print(f"Error creating bucket: {str(e)}")

    print("Database and storage setup completed!")