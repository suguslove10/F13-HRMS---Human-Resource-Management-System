from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
import io

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/')
def list_documents():
    s3 = boto3.client('s3',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )
    
    try:
        response = s3.list_objects_v2(Bucket=current_app.config['S3_BUCKET'])
        documents = response.get('Contents', [])
        return render_template('documents/list.html', documents=documents)
    except ClientError as e:
        flash(f"Error fetching documents: {str(e)}", 'danger')
        return render_template('documents/list.html', documents=[])

@bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if file:
            s3 = boto3.client('s3',
                region_name=current_app.config['AWS_REGION'],
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
                aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
            )
            
            try:
                # Generate a unique filename
                file_id = str(uuid.uuid4())
                original_filename = file.filename
                file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
                new_filename = f"{file_id}.{file_extension}"
                
                # Add metadata
                metadata = {
                    'original_filename': original_filename,
                    'document_type': request.form.get('document_type', 'OTHER'),
                    'description': request.form.get('description', ''),
                    'upload_date': datetime.now().isoformat()
                }
                
                # Upload file with metadata
                s3.upload_fileobj(
                    file,
                    current_app.config['S3_BUCKET'],
                    new_filename,
                    ExtraArgs={
                        'Metadata': metadata,
                        'ContentType': file.content_type
                    }
                )
                
                flash('Document uploaded successfully!', 'success')
                return redirect(url_for('documents.list_documents'))
            except ClientError as e:
                flash(f"Error uploading document: {str(e)}", 'danger')
                
    return render_template('documents/upload.html')

@bp.route('/download/<path:key>')
def download_document(key):
    try:
        s3 = boto3.client('s3',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        
        # Get the file from S3
        file_obj = s3.get_object(Bucket=current_app.config['S3_BUCKET'], Key=key)
        
        # Get metadata to find original filename
        metadata = file_obj.get('Metadata', {})
        original_filename = metadata.get('original_filename', key)
        
        # Create a file-like object to send
        file_data = io.BytesIO(file_obj['Body'].read())
        
        # Send the file
        return send_file(
            file_data,
            download_name=original_filename,
            as_attachment=True,
            mimetype=file_obj['ContentType']
        )
        
    except ClientError as e:
        flash(f"Error downloading document: {str(e)}", 'danger')
        return redirect(url_for('documents.list_documents'))

@bp.route('/delete/<path:key>', methods=['POST'])
def delete_document(key):
    try:
        s3 = boto3.client('s3',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        
        # Delete the file from S3
        s3.delete_object(Bucket=current_app.config['S3_BUCKET'], Key=key)
        
        flash('Document deleted successfully!', 'success')
    except ClientError as e:
        flash(f"Error deleting document: {str(e)}", 'danger')
    
    return redirect(url_for('documents.list_documents'))