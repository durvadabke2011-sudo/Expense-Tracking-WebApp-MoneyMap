"""
MoneyMap – Flask + Firebase Edition
Entry point: registers blueprints and starts the server.
"""

import os
from flask import Flask
from auth import auth_bp
from routes import routes_bp
from reports import reports_bp

app = Flask(__name__)

# Read SECRET_KEY from environment variable
# Falls back to config.py for local development
secret = os.environ.get('SECRET_KEY')
if not secret:
    from config import SECRET_KEY
    secret = SECRET_KEY

app.secret_key = secret

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(reports_bp)

# Start the app
if __name__ == '__main__':
    print("🚀 Starting MoneyMap (Firebase Edition)...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)