from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
import bcrypt
from .auth_routes import admin_required, login_required

bp = Blueprint('employees', __name__, url_prefix='/employees')

@bp.route('/')
@login_required
def list_employees():
    dynamodb = boto3.resource('dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    table = dynamodb.Table(current_app.config['EMPLOYEE_TABLE'])
    
    try:
        response = table.scan()
        employees = response.get('Items', [])
        return render_template('employees/list.html', employees=employees)
    except ClientError as e:
        flash(f"Error fetching employees: {str(e)}", 'danger')
        return render_template('employees/list.html', employees=[])

@bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_employee():
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        employee_table = dynamodb.Table(current_app.config['EMPLOYEE_TABLE'])
        user_table = dynamodb.Table(current_app.config['USER_TABLE'])
        
        try:
            # Generate password hash
            password = "employee123"  # Default password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Create user entry
            user_id = str(uuid.uuid4())
            user_data = {
                'userId': user_id,
                'email': request.form['email'],
                'password': password_hash.decode('utf-8'),
                'role': 'EMPLOYEE',
                'firstName': request.form['firstName'],
                'lastName': request.form['lastName'],
                'createdAt': datetime.now().isoformat()
            }
            
            # Create employee entry
            employee_data = {
                'employeeId': user_id,
                'email': request.form['email'],
                'firstName': request.form['firstName'],
                'lastName': request.form['lastName'],
                'department': request.form['department'],
                'position': request.form['position'],
                'createdAt': datetime.now().isoformat()
            }
            
            # Save both entries
            user_table.put_item(Item=user_data)
            employee_table.put_item(Item=employee_data)
            
            flash(f'Employee created successfully! Default password is: {password}', 'success')
            return redirect(url_for('employees.list_employees'))
        except ClientError as e:
            flash(f"Error creating employee: {str(e)}", 'danger')
            
    return render_template('employees/create.html')

@bp.route('/delete/<string:employee_id>', methods=['POST'])
@admin_required
def delete_employee(employee_id):
    dynamodb = boto3.resource('dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    employee_table = dynamodb.Table(current_app.config['EMPLOYEE_TABLE'])
    user_table = dynamodb.Table(current_app.config['USER_TABLE'])
    
    try:
        # Delete from both tables
        employee_table.delete_item(Key={'employeeId': employee_id})
        user_table.delete_item(Key={'userId': employee_id})
        
        flash('Employee deleted successfully!', 'success')
    except ClientError as e:
        flash(f"Error deleting employee: {str(e)}", 'danger')
    
    return redirect(url_for('employees.list_employees'))