# locustfile.py

from locust import HttpUser, task, between

class DSATrackerUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None

    def on_start(self):
        """Called when a Locust user starts, used for logging in."""
        # A test user should be pre-registered in your database for this to work
        response = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "password123"
        })

        if response.status_code == 200:
            self.token = response.json().get("token")
        else:
            print(f"Login failed: {response.status_code} {response.text}")


    @task(4) # Make this task 4 times more likely to run
    def get_questions(self):
        """Task to get questions, simulating user filtering."""
        if not self.token:
            return
        
        self.client.get(
            "/api/questions?topic=Arrays&difficulty=Easy",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/questions" # Group different filters under one name in stats
        )

    @task(1) # Make this task less likely
    def get_dashboard(self):
        """Task to load the main dashboard page."""
        if not self.token:
            return
            
        # CORRECTED: The dashboard is at /dashboard, not /api/dashboard
        self.client.get(
            "/dashboard", 
            headers={"Authorization": f"Bearer {self.token}"}
        )