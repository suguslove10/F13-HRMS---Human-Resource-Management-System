from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import boto3
from botocore.exceptions import ClientError
import bcrypt
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        if session['user'].get('role') != 'ADMIN':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        dynamodb = boto3.resource('dynamodb',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        table = dynamodb.Table(current_app.config['USER_TABLE'])

        try:
            # Query using the email index
            response = table.query(
                IndexName='EmailIndex',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )

            if response['Items']:
                user = response['Items'][0]
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    session['user'] = {
                        'userId': user['userId'],
                        'email': user['email'],
                        'role': user['role'],
                        'firstName': user['firstName'],
                        'lastName': user['lastName']
                    }
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('dashboard.index'))
                    
            flash('Invalid email or password', 'danger')
            
        except ClientError as e:
            flash(f'Error during login: {str(e)}', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))