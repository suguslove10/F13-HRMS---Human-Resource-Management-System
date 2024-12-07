from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
from .auth_routes import login_required, admin_required

bp = Blueprint('leaves', __name__, url_prefix='/leaves')

@bp.route('/')
@login_required
def list_leaves():
    dynamodb = boto3.resource('dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    table = dynamodb.Table(current_app.config['LEAVE_TABLE'])
    
    try:
        if session['user']['role'] == 'ADMIN':
            # Admin sees all leaves
            response = table.scan()
            leaves = response.get('Items', [])
        else:
            # Employees see only their leaves
            response = table.query(
                IndexName='EmployeeIndex',
                KeyConditionExpression='employeeId = :eid',
                ExpressionAttributeValues={
                    ':eid': session['user']['userId']
                }
            )
            leaves = response.get('Items', [])
            
        return render_template('leaves/list.html', leaves=leaves)
    except ClientError as e:
        flash(f"Error fetching leaves: {str(e)}", 'danger')
        return render_template('leaves/list.html', leaves=[])

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_leave():
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        table = dynamodb.Table(current_app.config['LEAVE_TABLE'])
        
        try:
            leave_data = {
                'leaveId': str(uuid.uuid4()),
                'employeeId': session['user']['userId'],
                'employeeName': f"{session['user']['firstName']} {session['user']['lastName']}",
                'startDate': request.form['startDate'],
                'endDate': request.form['endDate'],
                'leaveType': request.form['leaveType'],
                'reason': request.form['reason'],
                'status': 'PENDING',
                'createdAt': datetime.now().isoformat()
            }
            
            table.put_item(Item=leave_data)
            flash('Leave request created successfully!', 'success')
            return redirect(url_for('leaves.list_leaves'))
        except ClientError as e:
            flash(f"Error creating leave request: {str(e)}", 'danger')
            
    return render_template('leaves/create.html')

@bp.route('/update-status/<string:leave_id>', methods=['POST'])
@admin_required
def update_status(leave_id):
    action = request.form.get('action')
    if action not in ['approve', 'reject']:
        flash('Invalid action', 'danger')
        return redirect(url_for('leaves.list_leaves'))
        
    dynamodb = boto3.resource('dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    table = dynamodb.Table(current_app.config['LEAVE_TABLE'])
    
    try:
        table.update_item(
            Key={'leaveId': leave_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'APPROVED' if action == 'approve' else 'REJECTED'}
        )
        
        flash(f'Leave request {action}d successfully!', 'success')
    except ClientError as e:
        flash(f"Error updating leave status: {str(e)}", 'danger')
        
    return redirect(url_for('dashboard.index'))