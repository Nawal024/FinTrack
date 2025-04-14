import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Ensure the data directory exists (for backward compatibility)
if not os.path.exists('data'):
    os.makedirs('data')
    
# Initialize data files if they don't exist (for backward compatibility)
from utils import initialize_data_files
initialize_data_files()

# Create database tables and migrate existing data
with app.app_context():
    db.create_all()
    
    # Import at this point to avoid circular imports
    from models import migrate_data_from_json_to_db
    
    # Migrate data from JSON files to database if needed
    migrate_data_from_json_to_db()
