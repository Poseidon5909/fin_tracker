import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from serverless_http import Handler
from app import app

# Create the handler for Netlify Functions
handler = Handler(app)
