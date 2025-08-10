from flask import Flask, render_template, redirect, url_for
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import os

from routes import questions_bp
from auth import auth_bp
from cache import init_redis

app = Flask(__name__)

# --- CONFIGURATION ---
# Load secret key from environment or use a default (not for production)
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "a-default-fallback-secret-key")

# Load MongoDB URI from environment
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# ADD THIS LINE FOR DEBUGGING
print(f"--- Attempting to connect to MongoDB with URI: {app.config['MONGO_URI']} ---")

# Load Redis config from environment variables for Docker compatibility
app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
app.config['REDIS_PORT'] = int(os.getenv('REDIS_PORT', 6379))

# --- INITIALIZATION ---
jwt = JWTManager(app)

# Initialize MongoDB client only if URI is provided
if app.config["MONGO_URI"]:
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.db = mongo_client.get_database('dsa_tracker')
else:
    # Handle case where MONGO_URI is not set
    app.db = None
    app.logger.error("MONGO_URI environment variable not set. Database functionality will be disabled.")

init_redis(app)

# --- BLUEPRINT REGISTRATION ---
app.register_blueprint(questions_bp)
app.register_blueprint(auth_bp)

# --- PAGE RENDERING ROUTES ---
@app.route("/")
def home():
    """Redirects to the login page."""
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET"])
def signup():
    """Renders the user signup page."""
    return render_template("signup.html")

@app.route("/login", methods=["GET"])
def login():
    """Renders the user login page."""
    return render_template("login.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Renders the main dashboard page shell.
    All dynamic data is loaded via JavaScript fetch calls from the page itself.
    """
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    """Renders the logout page which clears the token via Javascript."""
    return render_template("logout.html")

if __name__ == "__main__":
    # This block is for local development without Docker
    app.run(host='0.0.0.0', port=5000, debug=True)
