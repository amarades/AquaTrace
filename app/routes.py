"""
Routes for AquaTrace application
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, session, jsonify, send_file, current_app
import csv
import io

from app import db
from app.models import User, Farm, SensorData
from app.services import get_data, predict_risk, send_alert, monthly_prediction
from app.config import DEFAULT_THRESHOLDS

main_bp = Blueprint('main', __name__)

# =====================
# Helper Functions
# =====================
def api_error(message, status_code=400):
    """Standardized API error response"""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat()
    }), status_code

def api_success(data):
    """Standardized API success response"""
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
    """Landing page"""
    return render_template("main.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Email and password are required")

        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session["user_id"] = user.id
                session["user"] = user.email
                session["full_name"] = user.full_name
                current_app.logger.info(f"User logged in: {email}")
                return redirect("/farms")
            else:
                return render_template("login.html", error="Invalid email or password")
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return render_template("login.html", error="Login failed. Please try again.")

    return render_template("login.html")

@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """User registration"""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        # Validation
        if not all([email, full_name, password]):
            return render_template("signup.html", error="Email, name, and password are required")

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        if len(password) < 8:
            return render_template("signup.html", error="Password must be at least 8 characters")

        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered")

        try:
            user = User(email=email, full_name=full_name, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            session["user"] = user.email
            session["full_name"] = user.full_name
            
            current_app.logger.info(f"New user registered: {email}")
            return redirect("/farms")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Signup error: {str(e)}")
            return render_template("signup.html", error="Registration failed. Please try again.")

    return render_template("signup.html")

@main_bp.route("/farms", methods=["GET", "POST"])
def farms():
    """Farm management"""
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    user = User.query.get(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        
        # Handle farm deletion
        if action == "delete":
            farm_id = request.form.get("farm_id")
            try:
                farm = Farm.query.get_or_404(farm_id)
                
                # Security: Verify ownership
                if farm.user_id != user_id:
                    return api_error("Unauthorized", 403)
                
                db.session.delete(farm)
                db.session.commit()
                current_app.logger.info(f"Farm deleted: {farm.name} by user {user.email}")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Farm deletion error: {str(e)}")
                return render_template("farms.html", farms=user.farms.all(), 
                                     error="Failed to delete farm")
            return redirect("/farms")
        
        # Handle farm creation
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        fish_type = request.form.get("fish_type", "").strip()
        pond_size = request.form.get("pond_size", "0")

        if not name:
            return render_template("farms.html", farms=user.farms.all(), 
                                 error="Farm name is required")

        try:
            pond_size = float(pond_size) if pond_size else 0.0
        except ValueError:
            pond_size = 0.0

        try:
            new_farm = Farm(
                user_id=user_id,
                name=name,
                location=location,
                fish_type=fish_type,
                pond_size=pond_size,
                **DEFAULT_THRESHOLDS
            )
            db.session.add(new_farm)
            db.session.commit()
            current_app.logger.info(f"Farm created: {name} by user {user.email}")
            return redirect("/farms")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Farm creation error: {str(e)}")
            return render_template("farms.html", farms=user.farms.all(), 
                                 error="Failed to create farm")

    return render_template("farms.html", farms=user.farms.all())

@main_bp.route("/dashboard/<int:farm_id>")
def dashboard(farm_id):
    """Farm monitoring dashboard"""
    if "user_id" not in session:
        return redirect("/login")

    try:
        farm = Farm.query.get_or_404(farm_id)
        
        # Security: Verify ownership
        if farm.user_id != session["user_id"]:
            return api_error("Unauthorized access", 403)
        
        return render_template("dashboard.html", farm=farm)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        return redirect("/farms")

@main_bp.route("/api/data/<int:farm_id>")
def api_data(farm_id):
    """Get sensor data for specific farm"""
    try:
        # Verify farm exists and get thresholds
        farm = Farm.query.get_or_404(farm_id)
        
        # Get sensor data
        raw = get_data()
        if raw is None:
            return api_error("No sensor data available", 503)

        # Calculate risk
        risk = predict_risk(raw.get("temperature", 0), raw.get("turbidity", 0))

        # Build response
        data = {
            "temperature": raw.get("temperature"),
            "oxygen": raw.get("oxygen"),
            "ph": raw.get("ph"),
            "ammonia": raw.get("ammonia"),
            "turbidity": raw.get("turbidity"),
            "timestamp": raw.get("timestamp"),
            "risk": risk,
            "alert": "HIGH" in risk.upper(),
            "thresholds": {
                "temp_min": farm.temp_min,
                "temp_max": farm.temp_max,
                "oxygen_min": farm.oxygen_min,
                "ammonia_max": farm.ammonia_max,
                "turbidity_max": farm.turbidity_max
            }
        }

        # Save to database
        try:
            reading = SensorData(
                farm_id=farm_id,
                temperature=data["temperature"],
                oxygen=data["oxygen"],
                ph=data["ph"],
                ammonia=data["ammonia"],
                turbidity=data["turbidity"],
                risk_level=risk.split()[0]
            )
            db.session.add(reading)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to save sensor data: {str(e)}")

        # Send alert if needed
        if data["alert"] and farm.owner.phone:
            send_alert(
                farm.owner.phone,
                farm.name,
                "High Risk Detected",
                f"Temp: {data['temperature']}°C, Turbidity: {data['turbidity']} NTU",
                "Check thresholds"
            )

        return api_success(data)

    except Exception as e:
        current_app.logger.error(f"API data error: {str(e)}")
        return api_error("Failed to fetch sensor data", 500)

@main_bp.route("/api/predict/<int:farm_id>")
def api_predict(farm_id):
    """Get monthly prediction for farm"""
    if "user_id" not in session:
        return api_error("Unauthorized", 401)

    try:
        farm = Farm.query.get_or_404(farm_id)
        
        # Security check
        if farm.user_id != session["user_id"]:
            return api_error("Not your farm", 403)

        # Get latest sensor reading
        latest = farm.sensor_data.order_by(SensorData.timestamp.desc()).first()
        if not latest:
            return api_error("No sensor data available yet", 404)

        # Generate prediction
        pred = monthly_prediction(
            fish_type=farm.fish_type or "Tilapia",
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
    """Download sensor data as CSV"""
    if "user_id" not in session:
        return redirect("/login")

    try:
        farm = Farm.query.get_or_404(farm_id)
        
        if farm.user_id != session["user_id"]:
            return api_error("Unauthorized", 403)

        # Get all sensor data for this farm
        readings = farm.sensor_data.order_by(SensorData.timestamp.desc()).all()

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Temperature (°C)', 'Oxygen (mg/L)', 
                        'pH', 'Ammonia (mg/L)', 'Turbidity (NTU)', 'Risk Level'])
        
        for reading in readings:
            writer.writerow([
                reading.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                reading.temperature,
                reading.oxygen,
                reading.ph,
                reading.ammonia,
                reading.turbidity,
                reading.risk_level
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{farm.name}_data_{datetime.now().strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return redirect(f"/dashboard/{farm_id}")

@main_bp.route("/logout")
def logout():
    """User logout"""
    email = session.get("user")
    session.clear()
    if email:
        current_app.logger.info(f"User logged out: {email}")
    return redirect("/")

# =====================
# Error Handlers
# =====================

@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("404.html"), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    current_app.logger.error(f"Internal error: {str(error)}")
    return render_template("500.html"), 500
