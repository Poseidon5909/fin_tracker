import os
import sys

# Add the project root so the function can import the Flask app.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import serverless_wsgi

from app import app


def handler(event, context):
	return serverless_wsgi.handle_request(app, event, context)


def main(event, context):
	return handler(event, context)
