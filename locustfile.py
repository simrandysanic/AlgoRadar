from locust import HttpUser, task, constant_throughput

class DSATrackerUser(HttpUser):
    wait_time = constant_throughput(0.833)  # 8.33 req/s ÷ 10 users = 0.833 req/s/user

    def on_start(self):
        # Try logging in and store token
        response = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "securepassword123"
        })

        if response.status_code == 200 and "token" in response.json():
            self.token = response.json()["token"]
            print(f"[LOGIN SUCCESS] Token: {self.token}")
        else:
            self.token = None
            print(f"[LOGIN FAILED] Status: {response.status_code}, Response: {response.text}")

    @task
    def get_questions(self):
        if not self.token:
            return  # Skip if login failed
        self.client.get(
            "/api/questions?topic=Arrays&difficulty=Easy&solved=true",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task
    def get_dashboard(self):
        if not self.token:
            return  # Skip if login failed
        self.client.get(
            "/api/dashboard",
            headers={"Authorization": f"Bearer {self.token}"}
        )
