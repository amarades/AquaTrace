# 🐟 AquaTrace – Aquaculture Water Quality Monitoring System

**Real-time water quality monitoring, predictive analytics, and SMS alerts for fish farming operations.**

A comprehensive Flask-based web application for monitoring and managing aquaculture farms with real-time sensor data, risk assessment, and automated alerts.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [SMS Alerts Setup](#-sms-alerts-setup)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Functionality
- **Multi-Farm Management**: Monitor multiple ponds/farms from a single dashboard
- **Real-Time Monitoring**: Live sensor data updates every 3 seconds with interactive charts
- **User Authentication**: Secure signup/login system with password hashing
- **Data Logging**: All sensor readings stored in SQLite database for historical analysis
- **Data Export**: Download sensor data as CSV files for external analysis

### Sensor Integration
- **Simulation Mode**: Test the system without hardware using simulated sensor data
- **Hardware Mode**: Connect Arduino/ESP32 sensors via serial communication
- **Flexible Data Sources**: Easy switching between simulation and hardware modes

### Analytics & Alerts
- **Risk Assessment**: AI-based water quality prediction with 3-tier alerts (Safe/Moderate/High)
- **Monthly Predictions**: Species-specific growth forecasts based on current water conditions
- **SMS Notifications**: Emergency alerts via Twilio when thresholds are exceeded
- **Per-Farm Thresholds**: Customize alert thresholds for each farm and fish species

### User Interface
- **Interactive Dashboards**: Real-time charts using Chart.js
- **Responsive Design**: Works on desktop and mobile devices
- **Status Indicators**: Visual badges showing Normal/Warning/Danger states
- **Intuitive Navigation**: Clean, user-friendly interface

---

## 📁 Project Structure

```
AquaTrace/
├── app/                          # Main application package
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # Configuration management
│   ├── models.py                 # SQLAlchemy database models
│   ├── routes.py                 # All application routes (blueprint)
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py           # Service exports
│   │   ├── data_provider.py     # Data source selector
│   │   ├── simulator.py          # Simulated sensor readings
│   │   ├── hardware.py          # Real Arduino/ESP serial reader
│   │   ├── ml_predictor.py      # Risk prediction engine
│   │   ├── prediction.py        # Monthly forecasting logic
│   │   └── sms_alert.py         # SMS notifications (Twilio)
│   │
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base layout template
│   │   ├── main.html             # Landing page
│   │   ├── login.html            # Login page
│   │   ├── signup.html           # User registration
│   │   ├── farms.html            # Farm management
│   │   └── dashboard.html        # Real-time monitoring dashboard
│   │
│   └── static/                   # Static assets
│       ├── css/
│       │   ├── auth.css          # Authentication styling
│       │   └── dashboard.css     # Dashboard styling
│       ├── js/
│       │   ├── auth.js           # Form validation
│       │   └── dashboard.js      # Chart updates, live data fetching
│       └── assets/
│           └── icons/            # Logo and icons
│
├── instance/                     # Runtime data (gitignored)
│   └── aquatrace.db              # SQLite database
│
├── data/                         # Data files
│   ├── data.csv                  # Sample/export data
│   └── exports/                  # CSV export directory
│
├── logs/                         # Application logs (gitignored)
│   └── aquatrace.log             # Rotating log file
│
├── tests/                        # Test suite
│   └── __init__.py               # Test package
│
├── docs/                         # Documentation
│   └── README.md                 # This file
│
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── .gitignore                    # Git ignore rules
```

---

## 🏗️ Architecture

### Application Factory Pattern
The application uses Flask's application factory pattern for better testability and configuration management:

```python
from app import create_app
app = create_app()
```

### Blueprint-Based Routing
All routes are organized in a single blueprint (`main_bp`) for better code organization:

```python
from app.routes import main_bp
app.register_blueprint(main_bp)
```

### Service Layer
Business logic is separated into a services layer:
- **Data Provider**: Abstracts data source (simulator vs hardware)
- **ML Predictor**: Risk assessment algorithms
- **Prediction Engine**: Monthly forecasting
- **SMS Alert**: Notification system

### Database Models
- **User**: Account management with password hashing
- **Farm**: Farm/pond profiles with customizable thresholds
- **SensorData**: Historical sensor readings with timestamps

---

## 🚀 Installation

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **pip** package manager
- **Virtual environment** (highly recommended)
- **Git** (for cloning)

### Step-by-Step Setup

#### 1. Clone or Download the Project
```bash
cd AquaTrace
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your SECRET_KEY
# Generate a secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

Minimum required in `.env`:
```env
SECRET_KEY=your-generated-secret-key-here
MODE=SIMULATION
```

#### 5. Initialize Database
The database will be created automatically on first run, but you can initialize it manually:
```bash
python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"
```

#### 6. Run the Application
```bash
python run.py
```

The server will start at `http://localhost:5000`

#### 7. Access the Application
- Open your browser and navigate to `http://localhost:5000`
- Sign up for a new account or use the demo account:
  - Email: `demo@aquatrace.com`
  - Password: `Demo@12345`

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

#### Required
```env
# Flask Secret Key (REQUIRED)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here
```

#### Application Mode
```env
# Options: SIMULATION (for testing) or HARDWARE (for real sensors)
MODE=SIMULATION
```

#### Hardware Settings (only used when MODE=HARDWARE)
```env
SERIAL_PORT=COM3              # Windows: COM3, Linux: /dev/ttyUSB0
SERIAL_BAUD=9600              # Serial communication baud rate
SERIAL_TIMEOUT=1.5            # Serial read timeout in seconds
```

#### Twilio SMS Alerts (Optional)
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_FROM=+1234567890    # Must be a verified Twilio number
```

#### Flask Environment
```env
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=INFO
```

### Configuration File (app/config.py)

The `config.py` file contains default thresholds and settings:

```python
DEFAULT_THRESHOLDS = {
    "temp_min": 15.0,      # Minimum temperature (°C)
    "temp_max": 32.0,      # Maximum temperature (°C)
    "oxygen_min": 5.0,      # Minimum dissolved oxygen (mg/L)
    "ammonia_max": 0.1,    # Maximum ammonia (mg/L)
    "turbidity_max": 1200.0 # Maximum turbidity (NTU)
}
```

These thresholds can be customized per farm when creating a new farm.

### Sensor Data Format (Hardware Mode)

When using hardware mode, sensors should send data in CSV format via serial:

```
temperature,oxygen,ph,ammonia,turbidity
```

Example:
```
25.5,6.2,7.1,0.08,450
```

- **Temperature**: Celsius (°C)
- **Oxygen**: Dissolved oxygen (mg/L)
- **pH**: pH level (0-14)
- **Ammonia**: Ammonia concentration (mg/L)
- **Turbidity**: Turbidity (NTU)

---

## 📖 Usage Guide

### 1. User Registration & Login

#### Sign Up
1. Navigate to `http://localhost:5000/signup`
2. Fill in the registration form:
   - Email address (used as username)
   - Full name
   - Phone number (optional, required for SMS alerts)
   - Password (minimum 8 characters)
   - Confirm password
3. Click "Sign Up"
4. You'll be automatically logged in and redirected to the farms page

#### Login
1. Navigate to `http://localhost:5000/login`
2. Enter your email and password
3. Click "Login"
4. You'll be redirected to your farms dashboard

### 2. Farm Management

#### Create a Farm
1. From the farms page, click "Add Farm"
2. Fill in farm details:
   - **Farm Name**: A descriptive name (e.g., "Tilapia Pond #1")
   - **Location**: Physical location (optional)
   - **Fish Type**: Species (Tilapia, Catfish, Trout, Carp, etc.)
   - **Pond Size**: Size in cubic meters (optional)
3. Click "Create Farm"
4. The farm will be created with default thresholds

#### Delete a Farm
1. From the farms list, click "Delete" on the farm you want to remove
2. Confirm the deletion
3. All associated sensor data will also be deleted

### 3. Monitoring Dashboard

#### Access Dashboard
1. From the farms page, click "Monitor" on any farm
2. The dashboard will load with real-time sensor data

#### Dashboard Features
- **Real-Time Charts**: Four interactive charts showing:
  - Temperature over time
  - Dissolved oxygen levels
  - pH values
  - Ammonia concentrations
- **Status Badges**: Visual indicators showing:
  - 🟢 Normal: All parameters within safe ranges
  - 🟡 Warning: Some parameters approaching limits
  - 🔴 Danger: Parameters exceed thresholds
- **Auto-Refresh**: Data updates every 3 seconds automatically
- **Risk Assessment**: Current risk level displayed prominently

#### Export Data
1. Click "Export CSV" button on the dashboard
2. A CSV file will be downloaded with all historical sensor readings
3. File format: `{farm_name}_data_{date}.csv`

### 4. Monthly Predictions

Access predictions via the API endpoint:
```
GET /api/predict/<farm_id>
```

Returns:
- Health score (0-100)
- Predicted monthly growth
- Recommendations for improvement
- Current vs optimal parameter ranges

---

## 🔌 API Documentation

### Authentication
Most endpoints require user authentication via session cookies. Login first to establish a session.

### Endpoints

#### Public Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/` | Landing page | HTML |
| GET | `/login` | Login page | HTML |
| POST | `/login` | User login | Redirect |
| GET | `/signup` | Registration page | HTML |
| POST | `/signup` | Create account | Redirect |

#### Protected Endpoints (Require Login)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/farms` | List user's farms | HTML |
| POST | `/farms` | Create/delete farm | Redirect |
| GET | `/dashboard/<farm_id>` | Farm monitoring dashboard | HTML |
| GET | `/api/data/<farm_id>` | Get latest sensor data | JSON |
| GET | `/api/predict/<farm_id>` | Get monthly prediction | JSON |
| GET | `/download/<farm_id>` | Download CSV data | CSV file |
| GET | `/logout` | User logout | Redirect |

### API Response Examples

#### GET /api/data/<farm_id>
```json
{
  "success": true,
  "data": {
    "temperature": 25.3,
    "oxygen": 6.5,
    "ph": 7.1,
    "ammonia": 0.08,
    "turbidity": 450,
    "timestamp": "Jan 22, 2026 14:30:45",
    "risk": "SAFE ✅",
    "alert": false,
    "thresholds": {
      "temp_min": 15.0,
      "temp_max": 32.0,
      "oxygen_min": 5.0,
      "ammonia_max": 0.1,
      "turbidity_max": 1200.0
    }
  },
  "timestamp": "2026-01-22T14:30:45.123456"
}
```

#### GET /api/predict/<farm_id>
```json
{
  "success": true,
  "data": {
    "fish_type": "Tilapia",
    "health_score": 85.5,
    "predicted_monthly_growth_kg": 4.25,
    "recommendation": "Excellent conditions. Continue current maintenance schedule.",
    "current_parameters": {
      "temperature": 27.0,
      "oxygen": 6.2,
      "ammonia": 0.03
    },
    "optimal_ranges": {
      "temp": [26, 29],
      "oxygen": [5, 8],
      "ammonia": [0, 0.05]
    }
  },
  "timestamp": "2026-01-22T14:30:45.123456"
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message here",
  "timestamp": "2026-01-22T14:30:45.123456"
}
```

---

## 🗄️ Database Schema

### User Model
```python
id: Integer (Primary Key)
email: String(120) (Unique, Indexed)
password_hash: String(200)
full_name: String(120)
phone: String(20)
created_at: DateTime
```

**Relationships:**
- One-to-Many: User → Farms

### Farm Model
```python
id: Integer (Primary Key)
user_id: Integer (Foreign Key → User.id, Indexed)
name: String(120)
location: String(200)
fish_type: String(50)
pond_size: Float
created_at: DateTime

# Alert Thresholds
temp_min: Float (default: 15.0)
temp_max: Float (default: 32.0)
oxygen_min: Float (default: 5.0)
ammonia_max: Float (default: 0.1)
turbidity_max: Float (default: 1200.0)
```

**Relationships:**
- Many-to-One: Farm → User
- One-to-Many: Farm → SensorData

### SensorData Model
```python
id: Integer (Primary Key)
farm_id: Integer (Foreign Key → Farm.id, Indexed)
temperature: Float
oxygen: Float
ph: Float
ammonia: Float
turbidity: Float
risk_level: String(20)  # SAFE, MODERATE, HIGH
timestamp: DateTime (Indexed)
```

**Relationships:**
- Many-to-One: SensorData → Farm

---

## 📱 SMS Alerts Setup

### Overview
SMS alerts are sent automatically when sensor data indicates high risk conditions. The system uses Twilio for SMS delivery.

### When Alerts Are Sent
- **Trigger**: When risk level is "HIGH RISK" and farm owner has a phone number
- **Cooldown**: 5 minutes between alerts for the same farm (prevents spam)
- **Location**: Triggered in `app/routes.py` when processing sensor data

### Alert Message Format
```
🚨 AquaTrace Alert
Farm: Tilapia Pond #1
Alert: High Risk Detected
Current: Temp: 33.5°C, Turbidity: 1300 NTU
Threshold: Check thresholds
Action: Check water quality immediately
```

### Setup Instructions

#### 1. Create Twilio Account
1. Sign up at [https://www.twilio.com](https://www.twilio.com)
2. Verify your email and phone number
3. Get your Account SID and Auth Token from the dashboard

#### 2. Get a Twilio Phone Number
1. In Twilio Console, go to Phone Numbers → Manage → Buy a number
2. Choose a number with SMS capabilities
3. Note the phone number in E.164 format (e.g., `+1234567890`)

#### 3. Configure Environment Variables
Add to your `.env` file:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_FROM=+1234567890
```

#### 4. Add Phone Number to User Profile
1. Ensure users have phone numbers in their profiles
2. Phone numbers should be in E.164 format: `+[country_code][number]`
3. Example: `+1234567890` (US), `+442071234567` (UK)

#### 5. Test SMS Functionality
1. Create a farm with high-risk thresholds
2. Trigger a high-risk condition (or wait for simulator to generate one)
3. Check that SMS is sent to the farm owner's phone

### Troubleshooting SMS

**SMS not sending:**
- Verify Twilio credentials are correct in `.env`
- Check phone number format (must be E.164: `+[country][number]`)
- Ensure Twilio account has sufficient balance
- Verify the "From" number is a valid Twilio number
- Check application logs for error messages

**Authentication errors:**
- Verify Account SID and Auth Token are correct
- Ensure credentials haven't been rotated/changed

**Cooldown active:**
- Wait 5 minutes between alerts for the same farm
- This is intentional to prevent SMS spam

---

## 🧠 Risk Prediction Algorithm

### Risk Assessment Logic

The system uses a simple but effective algorithm to assess water quality risk:

#### Risk Levels
- **SAFE ✅**: All parameters within acceptable ranges
- **MODERATE ⚠️**: Some parameters approaching limits
- **HIGH 🚨**: Parameters exceed thresholds

#### Calculation (ml_predictor.py)
```python
if temp > 32 or turb > 1200:
    return "HIGH RISK ⚠️"
elif temp > 30 or turb > 900:
    return "MODERATE RISK ⚠️"
return "SAFE ✅"
```

### Monthly Prediction Algorithm

The monthly prediction uses species-specific optimal ranges:

#### Health Score Calculation (0-100)
- **Base Score**: 100 points
- **Temperature Deviation**: -2 points per °C outside optimal range
- **Low Oxygen**: -10 points per mg/L below minimum
- **High Oxygen**: -5 points per mg/L above maximum
- **High Ammonia**: -100 points per mg/L above maximum
- **Final Score**: Clamped between 0 and 100

#### Species-Specific Ranges

**Tilapia:**
- Temperature: 26-29°C
- Oxygen: 5-8 mg/L
- Ammonia: 0-0.05 mg/L

**Catfish:**
- Temperature: 23-27°C
- Oxygen: 4-7 mg/L
- Ammonia: 0-0.08 mg/L

**Trout:**
- Temperature: 10-15°C
- Oxygen: 6-9 mg/L
- Ammonia: 0-0.02 mg/L

#### Growth Prediction
```
Predicted Growth = Base Growth × (Health Score / 100)
```

Base growth rates:
- Tilapia: 5 kg/month per 100 fish
- Catfish: 6 kg/month per 100 fish
- Trout: 4 kg/month per 100 fish

---

## 💻 Development

### Running in Development Mode
```bash
python run.py
```

The application runs with:
- Debug mode enabled
- Auto-reload disabled (set `use_reloader=False` to avoid issues)
- Port 5000

### Project Structure Best Practices
- **Application Factory**: Use `create_app()` for better testing
- **Blueprints**: Routes organized in `app/routes.py`
- **Services Layer**: Business logic separated from routes
- **Configuration**: Centralized in `app/config.py`
- **Models**: Database models in `app/models.py`

### Adding New Features

#### Adding a New Route
1. Add route function to `app/routes.py`
2. Use `@main_bp.route()` decorator
3. Import necessary models and services

#### Adding a New Service
1. Create new file in `app/services/`
2. Add to `app/services/__init__.py` exports
3. Import in routes: `from app.services import your_service`

#### Adding a New Model
1. Add model class to `app/models.py`
2. Import `db` from `app`
3. Run database migration or recreate tables

### Testing
```bash
# Run tests (when test suite is added)
python -m pytest tests/
```

### Code Quality
```bash
# Format code (if black is installed)
black app/

# Lint code (if flake8 is installed)
flake8 app/
```

---

## 🚀 Deployment

### Production Considerations

#### 1. Environment Variables
- Set `FLASK_ENV=production`
- Set `FLASK_DEBUG=False`
- Use a strong `SECRET_KEY`
- Configure all required services (Twilio, etc.)

#### 2. Database
- Consider migrating from SQLite to PostgreSQL for production
- Set up database backups
- Use connection pooling

#### 3. Web Server
Use a production WSGI server:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### 4. Reverse Proxy
Use Nginx or Apache as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. Security
- Enable HTTPS with SSL certificates
- Use secure session cookies
- Implement CSRF protection
- Set up rate limiting
- Regular security updates

#### 6. Monitoring
- Set up application logging
- Monitor error rates
- Track performance metrics
- Set up alerts for critical issues

### Docker Deployment (Future)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

---

## 🐛 Troubleshooting

### Common Issues

#### "Database locked" Error
**Problem**: SQLite database is locked by another process.

**Solutions**:
- Close other connections to the database
- Delete `instance/aquatrace.db` and reinitialize
- Check for multiple Flask instances running
- Consider using PostgreSQL for production

#### SMS Not Sending
**Problem**: SMS alerts are not being sent.

**Solutions**:
- Verify Twilio credentials in `.env`
- Check phone number format: `+[country_code][number]`
- Ensure Twilio account has sufficient balance
- Verify `TWILIO_PHONE_FROM` is a valid Twilio number
- Check application logs for error messages
- Test with a verified phone number first

#### No Sensor Data (Hardware Mode)
**Problem**: No data received from hardware sensors.

**Solutions**:
- Verify serial port: `python -c "import serial; s=serial.Serial('COM3', 9600); print(s.readline())"`
- Check serial data format matches: `temp,oxygen,ph,ammonia,turbidity`
- Verify baud rate matches sensor configuration
- Check cable connections
- Try simulator mode first: `MODE=SIMULATION`
- Check Windows Device Manager for COM port number

#### Dashboard Not Updating
**Problem**: Dashboard shows stale data or doesn't update.

**Solutions**:
- Check browser console for JavaScript errors (F12)
- Verify `/api/data/<farm_id>` endpoint returns JSON
- Clear browser cache and refresh
- Check network tab for failed requests
- Verify farm_id in URL is correct
- Check server logs for errors

#### Import Errors After Restructuring
**Problem**: Module import errors.

**Solutions**:
- Ensure you're running from project root: `python run.py`
- Verify all `__init__.py` files exist in packages
- Check import paths use `app.` prefix
- Clear `__pycache__` directories: `find . -type d -name __pycache__ -exec rm -r {} +`
- Reinstall dependencies: `pip install -r requirements.txt`

#### Port Already in Use
**Problem**: Port 5000 is already in use.

**Solutions**:
- Find process using port: `netstat -ano | findstr :5000` (Windows)
- Kill the process or use a different port
- Change port in `run.py`: `app.run(port=5001)`

### Getting Help

1. **Check Logs**: Review `logs/aquatrace.log` for error messages
2. **Browser Console**: Check browser developer tools (F12) for JavaScript errors
3. **Server Output**: Check terminal output when running the server
4. **Database**: Verify database integrity and connections

---

## 🤝 Contributing

### How to Contribute

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Follow code style and add tests
4. **Commit Changes**: `git commit -m 'Add amazing feature'`
5. **Push to Branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex logic

### Reporting Issues
When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

---

## 📝 License

This project is open-source and available for educational and commercial use.

---

## 📞 Support

For issues, feature requests, or contributions:
- Create an issue on GitHub
- Email: support@aquatrace.com

---

## 🎯 Future Enhancements

- [ ] Machine Learning model for predictive maintenance
- [ ] Mobile app (React Native)
- [ ] Integration with IoT platforms (AWS IoT, Azure IoT)
- [ ] Multi-language support
- [ ] Advanced data visualization (3D charts, heatmaps)
- [ ] Export to Excel with charts
- [ ] Email notifications in addition to SMS
- [ ] User roles and permissions
- [ ] API authentication (JWT tokens)
- [ ] Real-time WebSocket updates
- [ ] Historical data analysis and trends
- [ ] Automated report generation

---

**Happy Monitoring! 🐟💧**

*Last Updated: January 2026*
