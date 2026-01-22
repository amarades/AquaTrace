"""
Entry point for AquaTrace application

This is the main entry point for running the AquaTrace Flask application.
Run this file to start the development server.

Usage:
    python run.py

The server will start on http://localhost:5000
"""
from app import create_app

# Create the Flask application using the application factory
# This pattern allows for better testing and configuration management
app = create_app()

# Only run the server if this file is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    # Start the Flask development server
    # debug=True: Enables debug mode (shows detailed error pages, auto-reload)
    # use_reloader=False: Disables auto-reload to avoid issues with serial ports
    # port=5000: Server listens on port 5000
    app.run(debug=True, use_reloader=False, port=5000)
