"""
PedalPower - Smart Pedal-Powered Electricity Generation System
--------------------------------------------------------------
STARTUP INSTRUCTIONS:
1. pip install flask flask-cors flask-sqlalchemy flask-login werkzeug requests
2. python setup_vendor.py
3. python app.py
"""

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config
from models.models import db, User
from routes.auth import auth as auth_blueprint
from routes.main import main as main_blueprint
from routes.api import api as api_blueprint
import sqlalchemy as sa

def run_migrations(app):
    """Simple migration helper to add missing columns to existing database."""
    with app.app_context():
        engine = db.engine
        inspector = sa.inspect(engine)
        
        # Check PedalSession table
        columns = [c['name'] for c in inspector.get_columns('pedal_session')]
        
        with engine.connect() as conn:
            if 'raw_rpm' not in columns:
                conn.execute(sa.text('ALTER TABLE pedal_session ADD COLUMN raw_rpm FLOAT DEFAULT 0.0'))
            if 'raw_voltage' not in columns:
                conn.execute(sa.text('ALTER TABLE pedal_session ADD COLUMN raw_voltage FLOAT DEFAULT 0.0'))
            if 'raw_current' not in columns:
                conn.execute(sa.text('ALTER TABLE pedal_session ADD COLUMN raw_current FLOAT DEFAULT 0.0'))
            if 'power_w' not in columns:
                conn.execute(sa.text('ALTER TABLE pedal_session ADD COLUMN power_w FLOAT DEFAULT 0.0'))
            conn.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    # Run migrations before create_all
    run_migrations(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    print("-----------------------------------------------")
    print("PedalPower Server Started")
    print("Dashboard: http://127.0.0.1:5000")
    print("-----------------------------------------------")
    app.run(debug=True, port=5000)
