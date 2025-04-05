import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///recipes.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    # Import models and routes after app is created
    import models
    import routes
    
    # Create database tables
    db.create_all()
    
    # Create admin user if not exists
    from models import User, Cuisine
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpassword'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Admin user created')
    
    # Create default cuisines if they don't exist
    if Cuisine.query.count() == 0:
        # Create the four required cuisines
        cuisines = [
            Cuisine(name='Russian', description='Traditional Russian cuisine with hearty soups, stews, and dumplings.'),
            Cuisine(name='Armenian', description='Armenian cuisine features fresh herbs, spices, and slow-cooked dishes.'),
            Cuisine(name='Japanese', description='Japanese cuisine emphasizes fresh, seasonal ingredients with minimal preparation.'),
            Cuisine(name='Italian', description='Italian cuisine is known for its pasta, pizza, risotto, and regional specialties.')
        ]
        
        db.session.add_all(cuisines)
        db.session.commit()
        app.logger.info('Default cuisines created')

# Load user from session
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
