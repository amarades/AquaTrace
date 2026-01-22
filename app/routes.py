"""
Routes for AquaTrace application

This module contains all Flask routes (URL endpoints) for the application.
Routes are organized using Flask Blueprints for better code organization.

All routes are protected by session-based authentication except for
public pages (home, login, signup).
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, session, jsonify, send_file, current_app
import csv
import io

# Import database and models
from app import db
from app.models import User, Farm, SensorData

# Import service functions for business logic
from app.services import get_data, predict_risk, send_alert, monthly_prediction
from app.config import DEFAULT_THRESHOLDS

# Create a Blueprint to organize routes
# Blueprints allow grouping related routes together
main_bp = Blueprint('main', __name__)

# =====================
# Helper Functions
# =====================

def api_error(message, status_code=400):
    """
    Create a standardized JSON error response for API endpoints.
    
    Args:
        message: Error message to return to client
        status_code: HTTP status code (default: 400 Bad Request)
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat()  # ISO format timestamp
    }), status_code

def api_success(data):
    """
    Create a standardized JSON success response for API endpoints.
    
    Args:
        data: Data to return to client (dict or list)
    
    Returns:
        JSON response with success flag, data, and timestamp
    """
    return jsonify({
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

# =====================
# Routes
# =====================

@main_bp.route("/")
def home():
    """
    Landing page route - public page showing application information.
    
    Returns:
        HTML: Rendered main.html template
    """
    return render_template("main.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User login route - handles both GET (show form) and POST (process login).
    
    GET: Displays the login form
    POST: Validates credentials and creates user session
    
    Returns:
        HTML: Login page with optional error message
        Redirect: To /farms on successful login
    """
    # Handle POST request (form submission)
    if request.method == "POST":
        # Get and clean form data
        email = request.form.get("email", "").strip().lower()  # Normalize email to lowercase
        password = request.form.get("password", "")

        # Validate that both fields are provided
        if not email or not password:
            return render_template("login.html", error="Email and password are required")

        try:
            # Find user by email in database
            user = User.query.filter_by(email=email).first()
            
            # Check if user exists and password is correct
            # check_password() compares hashed password with provided password
            if user and user.check_password(password):
                # Create session variables to track logged-in user
                session["user_id"] = user.id
                session["user"] = user.email
                session["full_name"] = user.full_name
                
                # Log successful login
                current_app.logger.info(f"User logged in: {email}")
                
                # Redirect to farms page after successful login
                return redirect("/farms")
            else:
                # Invalid credentials - don't reveal which is wrong (security)
                return render_template("login.html", error="Invalid email or password")
        except Exception as e:
            # Log error but don't expose details to user
            current_app.logger.error(f"Login error: {str(e)}")
            return render_template("login.html", error="Login failed. Please try again.")

    # Handle GET request - show login form
    return render_template("login.html")

@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    User registration route - handles both GET (show form) and POST (create account).
    
    GET: Displays the registration form
    POST: Validates input and creates new user account
    
    Returns:
        HTML: Signup page with optional error message
        Redirect: To /farms on successful registration
    """
    # Handle POST request (form submission)
    if request.method == "POST":
        # Get and clean all form fields
        email = request.form.get("email", "").strip().lower()  # Normalize email
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()  # Optional field
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        # =====================
        # Input Validation
        # =====================
        
        # Check required fields are provided
        if not all([email, full_name, password]):
            return render_template("signup.html", error="Email, name, and password are required")

        # Verify passwords match
        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        # Enforce minimum password length (security best practice)
        if len(password) < 8:
            return render_template("signup.html", error="Password must be at least 8 characters")

        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered")

        # =====================
        # Create User Account
        # =====================
        
        try:
            # Create new User object
            user = User(email=email, full_name=full_name, phone=phone)
            
            # Hash password before storing (never store plain text passwords)
            user.set_password(password)
            
            # Add to database session
            db.session.add(user)
            db.session.commit()  # Save to database

            # Automatically log in the new user
            session["user_id"] = user.id
            session["user"] = user.email
            session["full_name"] = user.full_name
            
            # Log successful registration
            current_app.logger.info(f"New user registered: {email}")
            
            # Redirect to farms page
            return redirect("/farms")

        except Exception as e:
            # Rollback database transaction on error
            db.session.rollback()
            current_app.logger.error(f"Signup error: {str(e)}")
            return render_template("signup.html", error="Registration failed. Please try again.")

    # Handle GET request - show registration form
    return render_template("signup.html")

@main_bp.route("/farms", methods=["GET", "POST"])
def farms():
    """
    Farm management route - list, create, and delete farms.
    
    GET: Displays list of user's farms
    POST: Creates new farm or deletes existing farm
    
    Returns:
        HTML: Farms management page
        Redirect: After successful create/delete
    """
    # Check if user is logged in (session-based authentication)
    if "user_id" not in session:
        return redirect("/login")

    # Get current user from database
    user_id = session["user_id"]
    user = User.query.get(user_id)

    # Handle POST request (form submission)
    if request.method == "POST":
        action = request.form.get("action")  # "delete" or None (create)
        
        # =====================
        # Handle Farm Deletion
        # =====================
        if action == "delete":
            farm_id = request.form.get("farm_id")
            try:
                # Get farm from database (404 if not found)
                farm = Farm.query.get_or_404(farm_id)
                
                # Security check: Verify user owns this farm
                # Prevents users from deleting other users' farms
                if farm.user_id != user_id:
                    return api_error("Unauthorized", 403)
                
                # Delete farm (cascade deletes associated sensor data)
                db.session.delete(farm)
                db.session.commit()
                current_app.logger.info(f"Farm deleted: {farm.name} by user {user.email}")
            except Exception as e:
                # Rollback on error
                db.session.rollback()
                current_app.logger.error(f"Farm deletion error: {str(e)}")
                return render_template("farms.html", farms=user.farms.all(), 
                                     error="Failed to delete farm")
            # Redirect to refresh the farms list
            return redirect("/farms")
        
        # =====================
        # Handle Farm Creation
        # =====================
        
        # Get form data
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        fish_type = request.form.get("fish_type", "").strip()
        pond_size = request.form.get("pond_size", "0")

        # Validate required field
        if not name:
            return render_template("farms.html", farms=user.farms.all(), 
                                 error="Farm name is required")

        # Convert pond_size to float, default to 0.0 if invalid
        try:
            pond_size = float(pond_size) if pond_size else 0.0
        except ValueError:
            pond_size = 0.0

        # Create new farm
        try:
            # Create Farm object with user_id and form data
            # **DEFAULT_THRESHOLDS unpacks default threshold values
            new_farm = Farm(
                user_id=user_id,
                name=name,
                location=location,
                fish_type=fish_type,
                pond_size=pond_size,
                **DEFAULT_THRESHOLDS  # Apply default alert thresholds
            )
            db.session.add(new_farm)
            db.session.commit()
            current_app.logger.info(f"Farm created: {name} by user {user.email}")
            return redirect("/farms")
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            current_app.logger.error(f"Farm creation error: {str(e)}")
            return render_template("farms.html", farms=user.farms.all(), 
                                 error="Failed to create farm")

    # Handle GET request - show farms list
    # user.farms.all() gets all farms belonging to this user
    return render_template("farms.html", farms=user.farms.all())

@main_bp.route("/dashboard/<int:farm_id>")
def dashboard(farm_id):
    """
    Farm monitoring dashboard - displays real-time sensor data.
    
    Args:
        farm_id: ID of the farm to monitor
    
    Returns:
        HTML: Dashboard page with real-time charts
        Redirect: To /farms if error or unauthorized
    """
    # Check authentication
    if "user_id" not in session:
        return redirect("/login")

    try:
        # Get farm from database (404 if not found)
        farm = Farm.query.get_or_404(farm_id)
        
        # Security check: Verify user owns this farm
        # Prevents users from viewing other users' farms
        if farm.user_id != session["user_id"]:
            return api_error("Unauthorized access", 403)
        
        # Render dashboard template with farm data
        # The dashboard JavaScript will fetch sensor data via /api/data endpoint
        return render_template("dashboard.html", farm=farm)
    except Exception as e:
        # Log error and redirect to farms page
        current_app.logger.error(f"Dashboard error: {str(e)}")
        return redirect("/farms")

@main_bp.route("/api/data/<int:farm_id>")
def api_data(farm_id):
    """
    API endpoint to get latest sensor data for a farm.
    
    This endpoint:
    1. Fetches current sensor readings (from simulator or hardware)
    2. Calculates risk level
    3. Saves reading to database
    4. Sends SMS alert if high risk detected
    
    Args:
        farm_id: ID of the farm to get data for
    
    Returns:
        JSON: Sensor data with risk assessment and thresholds
    """
    try:
        # Verify farm exists and get farm object (includes thresholds)
        farm = Farm.query.get_or_404(farm_id)
        
        # =====================
        # Get Sensor Data
        # =====================
        # This calls either simulator or hardware module based on MODE config
        raw = get_data()
        if raw is None:
            return api_error("No sensor data available", 503)

        # =====================
        # Calculate Risk Level
        # =====================
        # Uses temperature and turbidity to determine risk (SAFE/MODERATE/HIGH)
        risk = predict_risk(raw.get("temperature", 0), raw.get("turbidity", 0))

        # =====================
        # Build Response Data
        # =====================
        data = {
            # Sensor readings
            "temperature": raw.get("temperature"),  # Celsius
            "oxygen": raw.get("oxygen"),            # mg/L
            "ph": raw.get("ph"),                    # pH level
            "ammonia": raw.get("ammonia"),          # mg/L
            "turbidity": raw.get("turbidity"),      # NTU
            "timestamp": raw.get("timestamp"),       # Formatted timestamp
            
            # Risk assessment
            "risk": risk,                           # Risk level string
            "alert": "HIGH" in risk.upper(),        # Boolean: true if high risk
            
            # Farm-specific thresholds for frontend validation
            "thresholds": {
                "temp_min": farm.temp_min,
                "temp_max": farm.temp_max,
                "oxygen_min": farm.oxygen_min,
                "ammonia_max": farm.ammonia_max,
                "turbidity_max": farm.turbidity_max
            }
        }

        # =====================
        # Save to Database
        # =====================
        # Store reading for historical analysis
        try:
            reading = SensorData(
                farm_id=farm_id,
                temperature=data["temperature"],
                oxygen=data["oxygen"],
                ph=data["ph"],
                ammonia=data["ammonia"],
                turbidity=data["turbidity"],
                risk_level=risk.split()[0]  # Extract "SAFE", "MODERATE", or "HIGH"
            )
            db.session.add(reading)
            db.session.commit()
        except Exception as e:
            # Don't fail the request if database save fails
            db.session.rollback()
            current_app.logger.error(f"Failed to save sensor data: {str(e)}")

        # =====================
        # Send SMS Alert
        # =====================
        # Only send if high risk AND farm owner has phone number
        if data["alert"] and farm.owner.phone:
            send_alert(
                farm.owner.phone,      # Recipient phone number
                farm.name,            # Farm name for context
                "High Risk Detected",  # Alert type
                f"Temp: {data['temperature']}°C, Turbidity: {data['turbidity']} NTU",  # Current values
                "Check thresholds"    # Action message
            )

        # Return JSON response
        return api_success(data)

    except Exception as e:
        # Log error and return error response
        current_app.logger.error(f"API data error: {str(e)}")
        return api_error("Failed to fetch sensor data", 500)

@main_bp.route("/api/predict/<int:farm_id>")
def api_predict(farm_id):
    """
    API endpoint to get monthly growth prediction for a farm.
    
    Uses latest sensor reading and fish species to predict:
    - Health score (0-100)
    - Monthly growth forecast
    - Recommendations
    
    Args:
        farm_id: ID of the farm to predict for
    
    Returns:
        JSON: Prediction data with health score and growth forecast
    """
    # Check authentication
    if "user_id" not in session:
        return api_error("Unauthorized", 401)

    try:
        # Get farm from database
        farm = Farm.query.get_or_404(farm_id)
        
        # Security check: Verify ownership
        if farm.user_id != session["user_id"]:
            return api_error("Not your farm", 403)

        # Get most recent sensor reading for this farm
        # order_by().first() gets the latest reading
        latest = farm.sensor_data.order_by(SensorData.timestamp.desc()).first()
        if not latest:
            return api_error("No sensor data available yet", 404)

        # Generate monthly prediction using prediction service
        # Uses fish species and current water parameters
        pred = monthly_prediction(
            fish_type=farm.fish_type or "Tilapia",  # Default to Tilapia if not specified
            temperature=latest.temperature,
            oxygen=latest.oxygen,
            ammonia=latest.ammonia
        )

        return api_success(pred)

    except Exception as e:
        current_app.logger.error(f"Prediction error: {str(e)}")
        return api_error("Failed to generate prediction", 500)

@main_bp.route("/download/<int:farm_id>")
def download(farm_id):
    """
    Download all sensor data for a farm as CSV file.
    
    Args:
        farm_id: ID of the farm to download data for
    
    Returns:
        CSV file: All historical sensor readings
        Redirect: To dashboard if error
    """
    # Check authentication
    if "user_id" not in session:
        return redirect("/login")

    try:
        # Get farm from database
        farm = Farm.query.get_or_404(farm_id)
        
        # Security check: Verify ownership
        if farm.user_id != session["user_id"]:
            return api_error("Unauthorized", 403)

        # Get all sensor readings for this farm, ordered by most recent first
        readings = farm.sensor_data.order_by(SensorData.timestamp.desc()).all()

        # =====================
        # Generate CSV File
        # =====================
        
        # Create in-memory file-like object
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write CSV header row
        writer.writerow(['Timestamp', 'Temperature (°C)', 'Oxygen (mg/L)', 
                        'pH', 'Ammonia (mg/L)', 'Turbidity (NTU)', 'Risk Level'])
        
        # Write each sensor reading as a row
        for reading in readings:
            writer.writerow([
                reading.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Format timestamp
                reading.temperature,
                reading.oxygen,
                reading.ph,
                reading.ammonia,
                reading.turbidity,
                reading.risk_level
            ])

        # Reset file pointer to beginning
        output.seek(0)
        
        # Send file as download
        # Converts string to bytes, sets MIME type, and attachment flag
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),  # Convert to bytes
            mimetype='text/csv',                             # Set MIME type
            as_attachment=True,                              # Force download
            download_name=f'{farm.name}_data_{datetime.now().strftime("%Y%m%d")}.csv'  # Filename
        )

    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return redirect(f"/dashboard/{farm_id}")

@main_bp.route("/logout")
def logout():
    """
    User logout route - clears session and redirects to home.
    
    Returns:
        Redirect: To home page after clearing session
    """
    # Get email before clearing session (for logging)
    email = session.get("user")
    
    # Clear all session data (logs user out)
    session.clear()
    
    # Log logout if email was available
    if email:
        current_app.logger.info(f"User logged out: {email}")
    
    # Redirect to home page
    return redirect("/")

# =====================
# Error Handlers
# =====================
# These functions handle HTTP error codes and display custom error pages

@main_bp.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.
    
    Called when a route doesn't exist or resource is not found.
    
    Args:
        error: The error object from Flask
    
    Returns:
        HTML: 404 error page with status code 404
    """
    return render_template("404.html"), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.
    
    Called when an unhandled exception occurs.
    Rolls back database transaction to prevent data corruption.
    
    Args:
        error: The error object from Flask
    
    Returns:
        HTML: 500 error page with status code 500
    """
    # Rollback any pending database transaction
    # Prevents database from being left in inconsistent state
    db.session.rollback()
    
    # Log the error for debugging
    current_app.logger.error(f"Internal error: {str(error)}")
    
    return render_template("500.html"), 500
