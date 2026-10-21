import os
from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask_login import current_user
from config import config_by_name
from app.extensions import db, login_manager
from app.metrics import metrics, sync_gauges


def create_app(config_name=None):
    """Application factory for Placement Management System."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure instance and upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    if 'UPLOAD_FOLDER' in app.config:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Initialize Prometheus metrics exporter
    # Setting export_defaults=True exports default Flask request count, latency, etc.
    metrics.init_app(app)

    # User loader callback for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Sync custom gauges right before scraping /metrics
    @app.before_request
    def refresh_metrics_on_scrape():
        if request.path == '/metrics':
            sync_gauges()

    # Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.company import company_bp
    from app.blueprints.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # Root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif current_user.is_company():
                return redirect(url_for('company.dashboard'))
            elif current_user.is_student():
                return redirect(url_for('student.dashboard'))
        return render_template('index.html')

    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "ok"}), 200

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
