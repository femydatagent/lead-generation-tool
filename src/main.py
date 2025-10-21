"""
Lead Generation Tool - Main Application

This is the main Flask application that powers the Lead Generation Tool.
It provides REST API endpoints for generating leads with AI-powered semantic analysis
and enrichment from multiple data sources.

Features:
    - Lead generation from Google Maps
    - Semantic analysis for Instagram and CNPJ extraction
    - Data enrichment from DataStone and Apify
    - Real-time job progress tracking
    - CSV export functionality

Author: Lead Generation Tool Team
License: MIT
"""

import os
import sys
# DON'T CHANGE THIS - Required for proper module resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.leads_smart import leads_bp

# Initialize Flask application with static folder configuration
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Application configuration
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Register API blueprints
# User management endpoints: /api/users
app.register_blueprint(user_bp, url_prefix='/api')
# Lead generation endpoints: /api/leads/generate, /api/leads/status, /api/leads/download
app.register_blueprint(leads_bp, url_prefix='/api/leads')

# Database configuration (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and create tables
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    Serve static files and SPA routing.

    This route serves the frontend single-page application (SPA) and handles
    client-side routing by always returning index.html for non-file paths.

    Args:
        path: URL path requested by the client

    Returns:
        The requested file if it exists, otherwise index.html for SPA routing

    Example:
        / -> index.html
        /some-spa-route -> index.html (for client-side routing)
        /style.css -> style.css (if exists)
    """
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    # If a specific file is requested and exists, serve it
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Otherwise, serve index.html for SPA routing
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Run the Flask development server
    # In production, use a WSGI server like Gunicorn or uWSGI
    app.run(host='0.0.0.0', port=5000, debug=True)
