"""
Database models for AquaTrace application

This module defines all database tables using SQLAlchemy ORM.
Models represent the data structure and relationships between entities.

Models:
    - User: User accounts with authentication
    - Farm: Farm/pond profiles with customizable thresholds
    - SensorData: Historical sensor readings
"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(db.Model):
    """
    User model - represents user accounts in the system.
    
    Stores user authentication information and profile data.
    Has a one-to-many relationship with Farm (one user can have many farms).
    """
    __tablename__ = 'users'  # Database table name
    
    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    
    # Email is used as username - must be unique and indexed for fast lookups
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Password hash (never store plain text passwords)
    # Uses Werkzeug's password hashing for security
    password_hash = db.Column(db.String(200), nullable=False)
    
    # User profile information
    full_name = db.Column(db.String(120))  # User's full name
    phone = db.Column(db.String(20))       # Phone number for SMS alerts (optional)
    
    # Timestamp when account was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    # One user can have many farms
    # lazy='dynamic' means farms are loaded as a query object (not all at once)
    # cascade='all, delete-orphan' means deleting a user deletes all their farms
    farms = db.relationship('Farm', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and store password securely.
        
        Uses Werkzeug's password hashing which includes salt and uses
        a secure hashing algorithm (PBKDF2 by default).
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify if provided password matches stored hash.
        
        Args:
            password: Plain text password to verify
        
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<User {self.email}>'


class Farm(db.Model):
    """
    Farm model - represents a fish farm/pond profile.
    
    Each farm belongs to one user and can have many sensor readings.
    Stores farm information and customizable alert thresholds.
    """
    __tablename__ = 'farms'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User - which user owns this farm
    # nullable=False means every farm must have an owner
    # index=True speeds up queries filtering by user_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Farm information
    name = db.Column(db.String(120), nullable=False)      # Farm name (required)
    location = db.Column(db.String(200))                    # Physical location (optional)
    fish_type = db.Column(db.String(50))                  # Species: 'Tilapia', 'Catfish', etc.
    pond_size = db.Column(db.Float)                       # Size in cubic meters (optional)
    
    # Timestamp when farm was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # =====================
    # Alert Thresholds
    # =====================
    # These values determine when alerts are triggered
    # Can be customized per farm (overrides defaults)
    temp_max = db.Column(db.Float, default=32.0)      # Maximum safe temperature (°C)
    temp_min = db.Column(db.Float, default=15.0)      # Minimum safe temperature (°C)
    oxygen_min = db.Column(db.Float, default=5.0)     # Minimum dissolved oxygen (mg/L)
    ammonia_max = db.Column(db.Float, default=0.1)     # Maximum safe ammonia (mg/L)
    turbidity_max = db.Column(db.Float, default=1200.0) # Maximum acceptable turbidity (NTU)
    
    # Relationships
    # One farm can have many sensor readings
    # lazy='dynamic' loads readings as query object
    # cascade='all, delete-orphan' deletes readings when farm is deleted
    sensor_data = db.relationship('SensorData', backref='farm', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<Farm {self.name}>'


class SensorData(db.Model):
    """
    SensorData model - stores historical sensor readings.
    
    Each reading belongs to one farm and contains all sensor measurements
    from a single point in time. Used for historical analysis and charts.
    """
    __tablename__ = 'sensor_data'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to Farm - which farm this reading belongs to
    # nullable=False means every reading must belong to a farm
    # index=True speeds up queries filtering by farm_id
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False, index=True)
    
    # =====================
    # Sensor Readings
    # =====================
    # All measurements from sensors at this point in time
    temperature = db.Column(db.Float, nullable=False)  # Water temperature in Celsius
    oxygen = db.Column(db.Float, nullable=False)       # Dissolved oxygen in mg/L
    ph = db.Column(db.Float, nullable=False)          # pH level (0-14 scale)
    ammonia = db.Column(db.Float, nullable=False)      # Ammonia concentration in mg/L
    turbidity = db.Column(db.Float, default=0.0)       # Turbidity in NTU (optional)
    
    # =====================
    # Metadata
    # =====================
    # Risk level calculated when reading was saved
    risk_level = db.Column(db.String(20))  # Values: 'SAFE', 'MODERATE', 'HIGH'
    
    # Timestamp when reading was taken
    # index=True speeds up time-based queries (e.g., "get latest reading")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<SensorData farm_id={self.farm_id} temp={self.temperature}>'
