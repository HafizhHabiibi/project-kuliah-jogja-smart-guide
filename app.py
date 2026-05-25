import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
from models.destination import Destination, seed_destinations
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.profile_controller import profile_bp
from controllers.admin_controller import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan masuk.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        seed_destinations()
        _seed_admin()

    return app


def _seed_admin():
    """Create default admin account if it doesn't exist."""
    admin = User.query.filter_by(email='admin@jogjasmartguide.com').first()
    if not admin:
        admin = User(
            username='Admin',
            email='admin@jogjasmartguide.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
