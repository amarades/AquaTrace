"""Database models for AquaTrace application"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(db.Model):
    """User model for account management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Farm(db.Model):
    """Farm/pond profile model"""
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    fish_type = db.Column(db.String(50))  # e.g., 'Tilapia', 'Catfish'
    pond_size = db.Column(db.Float)  # in cubic meters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Alert thresholds (optional per-farm overrides)
    temp_max = db.Column(db.Float, default=32.0)
    temp_min = db.Column(db.Float, default=15.0)
    oxygen_min = db.Column(db.Float, default=5.0)
    ammonia_max = db.Column(db.Float, default=0.1)
    turbidity_max = db.Column(db.Float, default=1200.0)
    
    # Relationships
    sensor_data = db.relationship('SensorData', backref='farm', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Farm {self.name}>'


class SensorData(db.Model):
    """Sensor readings storage"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False, index=True)
    
    # Sensor readings
    temperature = db.Column(db.Float, nullable=False)
    oxygen = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    ammonia = db.Column(db.Float, nullable=False)
    turbidity = db.Column(db.Float, default=0.0)
    
    # Metadata
    risk_level = db.Column(db.String(20))  # SAFE, MODERATE, HIGH
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SensorData farm_id={self.farm_id} temp={self.temperature}>'
