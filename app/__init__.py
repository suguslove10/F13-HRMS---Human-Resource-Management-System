from flask import Flask, redirect, url_for
from app.config import Config
import boto3
import secrets
import os
from dotenv import load_dotenv, set_key
from pathlib import Path
from app.utils.db_setup import create_tables_and_bucket

def create_app():
    app = Flask(__name__)
    
    # Update secret key if needed
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / '.env'
    
    if not env_path.exists():
        env_path.touch()
    
    load_dotenv(env_path)
    
    if not os.getenv('SECRET_KEY'):
        new_secret_key = secrets.token_urlsafe(32)
        set_key(env_path, 'SECRET_KEY', new_secret_key)
        
    app.config.from_object(Config)
    
    create_tables_and_bucket(app)
    
    # Register blueprints
    from app.routes import employee_routes, leave_routes, document_routes, auth_routes, dashboard_routes
    app.register_blueprint(employee_routes.bp)
    app.register_blueprint(leave_routes.bp)
    app.register_blueprint(document_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(dashboard_routes.bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))
    
    return app