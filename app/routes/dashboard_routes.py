from flask import Blueprint, render_template, current_app, session
import boto3
from botocore.exceptions import ClientError
from .auth_routes import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    dynamodb = boto3.resource('dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    
    # Initialize S3 client for document count
    s3 = boto3.client('s3',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    
    try:
        # Get employees count
        employee_table = dynamodb.Table(current_app.config['EMPLOYEE_TABLE'])
        employee_response = employee_table.scan(Select='COUNT')
        total_employees = employee_response.get('Count', 0)
        
        # Get leaves data
        leave_table = dynamodb.Table(current_app.config['LEAVE_TABLE'])
        leave_response = leave_table.scan()
        leaves = leave_response.get('Items', [])
        
        # Count different leave statuses
        pending_leaves = sum(1 for leave in leaves if leave.get('status') == 'PENDING')
        approved_leaves = sum(1 for leave in leaves if leave.get('status') == 'APPROVED')
        
        # Get document count from S3
        try:
            s3_response = s3.list_objects_v2(Bucket=current_app.config['S3_BUCKET'])
            total_documents = s3_response.get('KeyCount', 0)
        except ClientError:
            total_documents = 0
        
        # Get recent leaves with employee details
        recent_leaves = []
        for leave in sorted(leaves, key=lambda x: x.get('createdAt', ''), reverse=True)[:5]:
            # Get employee details for each leave
            try:
                emp_response = employee_table.get_item(
                    Key={'employeeId': leave.get('employeeId')}
                )
                employee = emp_response.get('Item', {})
                leave['employeeName'] = f"{employee.get('firstName', '')} {employee.get('lastName', '')}"
            except ClientError:
                leave['employeeName'] = leave.get('employeeId', 'Unknown')
            recent_leaves.append(leave)
        
        stats = {
            'total_employees': total_employees,
            'pending_leaves': pending_leaves,
            'approved_leaves': approved_leaves,
            'total_documents': total_documents
        }
        
        return render_template('dashboard/index.html', 
                             stats=stats,
                             recent_leaves=recent_leaves,
                             user=session.get('user', {}))
                             
    except ClientError as e:
        print(f"Error accessing AWS services: {str(e)}")
        stats = {
            'total_employees': 0,
            'pending_leaves': 0,
            'approved_leaves': 0,
            'total_documents': 0
        }
        return render_template('dashboard/index.html', 
                             stats=stats,
                             recent_leaves=[],
                             user=session.get('user', {}))