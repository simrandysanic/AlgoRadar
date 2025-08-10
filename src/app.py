from flask import Flask, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from collections import Counter
import json

from routes import questions_bp
from auth import auth_bp
from cache import init_redis

app = Flask(__name__)

# --- CONFIGURATION ---
app.config["JWT_SECRET_KEY"] = "supersecret"  # Use an environment variable in production
app.config["MONGO_URI"] = "mongodb+srv://dsa_user:simrandb@cluster0.4nrun5g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
app.config['REDIS_HOST'] = 'localhost'
app.config['REDIS_PORT'] = 6379

# --- INITIALIZATION ---
jwt = JWTManager(app)
mongo_client = MongoClient(app.config["MONGO_URI"])
app.db = mongo_client.get_database('dsa_tracker')
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
@jwt_required()
def dashboard():
    """
    Renders the main dashboard page.
    Fetches user data and calculates stats, with Redis caching.
    """
    user_id = get_jwt_identity()

    # Check Redis for cached dashboard data
    cache_key = f"dashboard:{user_id}"
    if current_app.redis:
        cached_dashboard = current_app.redis.get(cache_key)
        if cached_dashboard:
            current_app.logger.info(f"Dashboard cache hit for {user_id}")
            dashboard_data = json.loads(cached_dashboard)
            return render_template(
                "dashboard.html",
                chart_data=dashboard_data["chart_data"],
                total_problems=dashboard_data["total_problems"],
                streak=dashboard_data["streak"]
            )

    current_app.logger.info(f"Dashboard cache miss for {user_id}, fetching from MongoDB")

    # Fetch problems from MongoDB
    problems = list(current_app.db.questions.find({"user_id": ObjectId(user_id)}))

    # Prepare chart data (difficulty distribution)
    difficulty_counts = Counter([p.get('difficulty', 'Unknown') for p in problems])
    chart_data = {
        "labels": list(difficulty_counts.keys()),
        "datasets": [{
            "label": "Problems by Difficulty",
            "data": list(difficulty_counts.values()),
            "backgroundColor": ["#36A2EB", "#FFCE56", "#FF6384"]  # Easy, Medium, Hard
        }]
    }

    # Total problems
    total_problems = len(problems)

    # Current streak calculation (robust version)
    solved_dates = sorted({
        p.get("date_solved", "").split("T")[0]
        for p in problems if p.get("solved") and p.get("date_solved")
    })
    streak = 0
    if solved_dates:
        today = datetime.utcnow().date()
        # Iterate backwards from the most recent solved date
        for i in range(len(solved_dates) - 1, -1, -1):
            try:
                day = datetime.strptime(solved_dates[i], "%Y-%m-%d").date()
                # Check if the day is consecutive to the streak
                if (today - day).days == streak:
                    streak += 1
                else:
                    # If a day is missed, the streak is broken
                    break
            except ValueError:
                # Skip any malformed date strings
                continue

    # Store in Redis for 5 minutes
    if current_app.redis:
        dashboard_payload = {
            "chart_data": chart_data,
            "total_problems": total_problems,
            "streak": streak
        }
        current_app.redis.setex(cache_key, 300, json.dumps(dashboard_payload))

    return render_template(
        "dashboard.html",
        chart_data=chart_data,
        total_problems=total_problems,
        streak=streak
    )

@app.route("/logout")
def logout():
    """Renders the logout page which clears the token via Javascript."""
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)