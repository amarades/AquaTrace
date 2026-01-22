"""
AquaTrace - Aquaculture Water Quality Monitoring System
Flask Application Package

This module implements the Flask application factory pattern, which allows
for better testability and configuration management. The create_app() function
initializes and configures the Flask application with all necessary extensions.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
# This allows configuration without hardcoding sensitive values
load_dotenv()

# Initialize SQLAlchemy database extension
# This will be initialized with the Flask app in create_app()
db = SQLAlchemy()

def create_app():
    """
    Application factory pattern - creates and configures the Flask app instance.
    
    This function:
    1. Creates Flask app with template and static folder paths
    2. Configures database connection
    3. Sets up logging
    4. Registers blueprints (routes)
    5. Initializes database tables
    6. Creates demo user if needed
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    # template_folder and static_folder point to directories within the app package
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # =====================
    # Flask Configuration
    # =====================
    
    # SECRET_KEY is required for session management and CSRF protection
    # In production, this should be a strong random string from environment
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # =====================
    # Database Configuration
    # =====================
    
    # Get the project root directory (parent of app directory)
    # Then create instance directory for database storage
    INSTANCE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)  # Create directory if it doesn't exist
    
    # Set database path - SQLite database file
    DB_PATH = os.path.join(INSTANCE_PATH, 'aquatrace.db')
    
    # Configure SQLAlchemy database URI
    # SQLite is used for simplicity, but can be replaced with PostgreSQL/MySQL for production
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    
    # Disable SQLAlchemy event system (not needed, saves resources)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with Flask app
    # This connects SQLAlchemy to our Flask application
    db.init_app(app)
    
    # =====================
    # Logging Configuration
    # =====================
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    # Only set up file logging in production (not in debug mode)
    # In debug mode, errors are shown in console
    if not app.debug:
        # RotatingFileHandler automatically rotates logs when they get too large
        # maxBytes: Maximum log file size before rotation (10KB)
        # backupCount: Number of backup log files to keep
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'aquatrace.log'),
            maxBytes=10240,      # 10KB per log file
            backupCount=10       # Keep 10 backup files
        )
        
        # Set log message format: timestamp, level, message, file location
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Set logging level to INFO (logs info, warnings, errors)
        file_handler.setLevel(logging.INFO)
        
        # Add handler to Flask's logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AquaTrace startup')
    
    # =====================
    # Register Blueprints
    # =====================
    
    # Import and register the main blueprint containing all routes
    # Blueprints organize routes into modules for better code organization
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # =====================
    # Database Initialization
    # =====================
    
    # Create all database tables if they don't exist
    # This runs within app context to have access to db object
    with app.app_context():
        from app.models import User
        
        # Create all tables defined in models.py
        # This is safe to run multiple times - won't recreate existing tables
        db.create_all()
        
        # Create a demo user for testing purposes
        # Only creates if user doesn't already exist
        if not User.query.filter_by(email='demo@aquatrace.com').first():
            demo_user = User(
                email='demo@aquatrace.com',
                full_name='Demo User',
                phone='+234-xxx-xxx-xxxx'
            )
            # Hash the password before storing (security best practice)
            demo_user.set_password('Demo@12345')
            db.session.add(demo_user)
            db.session.commit()
            app.logger.info('Demo user created')
    
    # Return the configured Flask app
    return app
