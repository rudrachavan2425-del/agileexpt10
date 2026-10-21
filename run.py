import os
from app import create_app
from app.extensions import db

# Read configuration from environment or default
env_config = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_config)

# Auto-create tables if running directly or for initial startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))
