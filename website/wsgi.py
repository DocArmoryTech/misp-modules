#!/usr/bin/env python3
from app import create_app

# Create the Flask app using the factory
app = create_app()

if __name__ == "__main__":
    # Optional: Allow running wsgi.py directly for debugging
    app.run()
