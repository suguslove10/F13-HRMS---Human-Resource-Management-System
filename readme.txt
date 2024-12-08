# F13 HRMS - Human Resource Management System

A Flask-based HRMS application using AWS services (DynamoDB, S3) for data storage.

## Features
- User Authentication (Admin/Employee roles)
- Employee Management
- Leave Request Management
- Document Management
- Dashboard with Real-time Statistics

## Prerequisites
- Python 3.8 or higher
- AWS Account with access credentials
- pip (Python package manager)

## AWS Setup
1. Create an AWS account if you don't have one
2. Create an IAM user with access to:
   - DynamoDB
   - S3
3. Note down the AWS Access Key and Secret Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HRMS-Flask.git
cd HRMS-Flask
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory with your AWS credentials:
```env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
```

## Running the Application

1. Start the Flask application:
```bash
python run.py
```

2. Access the application at: `http://127.0.0.1:5000`

## Default Admin Login
- Email: admin@f13.com
- Password: admin123

## File Structure
```
HRMS-Flask/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── document_routes.py
│   │   ├── employee_routes.py
│   │   └── leave_routes.py
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── documents/
│   │   ├── employees/
│   │   ├── leaves/
│   │   └── base.html
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── utils/
│   │   └── db_setup.py
│   ├── __init__.py
│   └── config.py
├── venv/
├── .env
├── requirements.txt
├── run.py
└── README.md
```

## AWS Resources Created
The application automatically creates:
1. DynamoDB Tables:
   - F13_HRMS_Users
   - F13_HRMS_Employees
   - F13_HRMS_Leaves
2. S3 Bucket:
   - f13-hrms-documents

## Usage
1. First login with admin credentials
2. Create new employees (default password: employee123)
3. Employees can login and:
   - Request leaves
   - Upload documents
   - View their dashboard
4. Admin can:
   - Manage employees
   - Approve/reject leaves
   - Manage documents
   - View overall statistics

## Cleanup
To remove all AWS resources created by the application:
```bash
python cleanup.py
```

## Security Notes
- Change the default admin password after first login
- Update employee default passwords
- Do not commit the .env file
- Use proper security groups in production
- Enable HTTPS in production

## Development
1. To add new features:
   - Create new routes in app/routes/
   - Add templates in app/templates/
   - Update the database schema in utils/db_setup.py

2. To customize styles:
   - Modify app/static/css/style.css
   - Update templates as needed

## Troubleshooting
1. If tables don't create:
   - Check AWS credentials
   - Verify region settings
   - Check IAM permissions

2. If login fails:
   - Verify email and password
   - Check if user exists in DynamoDB
   - Clear browser cookies

## License
[MIT License](LICENSE)
