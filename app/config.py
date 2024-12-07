import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    AWS_REGION = 'ap-south-1'
    USER_TABLE = 'F13_HRMS_Users'
    EMPLOYEE_TABLE = 'F13_HRMS_Employees'
    LEAVE_TABLE = 'F13_HRMS_Leaves'
    S3_BUCKET = 'f13-hrms-documents'