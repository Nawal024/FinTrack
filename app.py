import os
import logging
from flask import Flask

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')
    
# Initialize data files if they don't exist
from utils import initialize_data_files
initialize_data_files()
