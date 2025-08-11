# AlgoRadar

**Live Site**: [https://algoradar.onrender.com](https://algoradar.onrender.com)

A full-stack web application designed to help developers track and visualize their progress while studying Data Structures and Algorithms.

---

### Key Features

* **Full User Authentication**: Secure user registration and login system using JWT.
* **Interactive Dashboard**: A central hub featuring a GitHub-style activity heatmap, a dynamic pie chart for difficulty breakdown, and a modern revision queue.
* **Complete Problem Management**: Full CRUD functionality for problems, managed through a rich modal interface that includes a CodeMirror editor, multi-tagging with autocomplete, and fields for complexity analysis.
* **Powerful Data Interaction**:
    * Full-text search across problem titles, notes, and tags.
    * Dynamic filtering by difficulty, status, and tags.
    * Clickable activity chart to view problems solved on a specific day.
* **Modern UI/UX**: A clean, responsive interface with persistent light and dark mode support.

---

### Tech Stack

* **Backend**: Python, Flask, Gunicorn
* **Frontend**: Vanilla JavaScript, HTML5, CSS3, Chart.js, CodeMirror
* **Database**: MongoDB Atlas
* **Caching**: Redis
* **Deployment & Containerization**: Docker, Render

---

### Running Locally

1.  Clone the repository.
2.  Create a `.env` file in the root directory and add your `MONGO_URI` and `SECRET_KEY`.
3.  Ensure Docker Desktop is running.
4.  Run the command: `docker-compose up --build`
5.  Access the application at `http://localhost:5000`.
