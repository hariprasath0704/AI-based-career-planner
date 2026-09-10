# PathPilot – AI Academic & Career Planner

PathPilot is an intelligent, full-stack college companion web application that helps students track subjects, academic deadlines, placement roadmaps, projects with milestone checklists, and resume milestones. It dynamically computes placement readiness scores and prioritizes study tasks using AI algorithms.

---

## 💻 Running PathPilot in Visual Studio Code (VS Code)

Follow these step-by-step instructions to run the application inside **VS Code**:

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** > **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the project folder:
   `c:\Users\harip_dg7cw87\Downloads\DNN  project\new my project path pilot`

---

### Step 2: Choose How to Run

#### Option A: One-Click F5 Debugging (Easiest)
1. Press **`F5`** on your keyboard (or click the **Run & Debug** icon `Ctrl + Shift + D` on the left sidebar).
2. Click the green ▶ **Play** button next to **"PathPilot: Run Flask App"**.
3. Open your browser to **[http://127.0.0.1:8080](http://127.0.0.1:8080)**.

#### Option B: Using VS Code Integrated Terminal
1. Open the terminal inside VS Code by pressing **`Ctrl + ~`** (or click **Terminal** > **New Terminal**).
2. Run the command:
   ```powershell
   py app.py 8080
   ```
3. Open your browser to **[http://127.0.0.1:8080](http://127.0.0.1:8080)**.

#### Option C: Running launcher batch script in Terminal
1. Open the terminal inside VS Code (`Ctrl + ~`).
2. Run:
   ```cmd
   .\run.bat
   ```
   *This automatically checks database tables, seeds default data, opens your web browser, and starts the web server on port 8080.*

---

## 🔑 Login Credentials
* **App URL:** [http://127.0.0.1:8080](http://127.0.0.1:8080)
* **Username:** `student`
* **Password:** `student123`

---

## 🌟 Key Features

1. **Academic Planner**:
   - Manage subjects, course credits, and target grades (S/O, A+, A, B).
   - Priority Task Agenda sorted into High, Medium, and Low Priority with deadline alerts (`Overdue`, `Due Today`, `Remaining Days`).
   - One-click `⚡ +30m Study` session logger.

2. **Project Tracker & Portfolio Planner**:
   - Sub-task milestones checklist that dynamically calculates project completion % in real-time.
   - One-click **Adopt AI Blueprint** to adopt job-track project templates into active portfolio.
   - Support for Live Demo links alongside GitHub codebase links.

3. **AI Recommendation System**:
   - Uses Scikit-learn's Cosine Similarity to compare the student's current skill profile against template career paths (e.g. Software Engineer, Web Developer, ML Engineer) to flag placement skill gaps and suggest next study actions.

4. **"What Should I Do Now?" Priority Finder**:
   - Evaluates assignments, tests, and weak skills using a mathematical priority heuristic:  
     `Priority = Urgency (Days until deadline) + Difficulty + Importance + Weakness Index + Job Track Relevance`.

5. **Circular Placement Readiness Gauge**:
   - Generates a score out of 100 representing academic standing (CGPA, arrears), core skills completed, projects completed, and resume completeness.

6. **Dynamic Daily Planner**:
   - Constructs a tailored timeline matching the student's available daily hours, utilizing 45-minute focus blocks and 15-minute breaks.

7. **Interactive Skill Roadmap**:
   - Visual map of skills grouped by Programming, Core CS, Development, AIML, and Placement.

8. **Unified Analytics Visuals**:
   - Renders Line and Bar charts using Chart.js to track study hours, subject progress, skill category coverage, and historic readiness scores.

---

## 📂 Project Directory Structure

```
path-pilot/
│
├── .vscode/
│   └── launch.json              # VS Code F5 Run & Debug configuration
├── app.py                       # Main Flask web server & page routing
├── models.py                    # Database schemas using Flask-SQLAlchemy
├── recommendation.py            # AI scoring models, cosine similarity, & scheduling
├── database_init.py             # Seeds default skills metadata & initial mock student
├── requirements.txt             # Project Python dependencies
├── run.bat                      # 1-Click launcher script for Windows
├── README.md                    # Setup and guide documentation (This file)
│
├── static/
│   ├── css/
│   │   └── style.css            # Responsive custom styles for dark/light mode
│   └── js/
│       ├── main.js              # Theme manager, scheduler completions, & AJAX triggers
│       └── charts.js            # Chart.js graphing configurations
│
└── templates/
    ├── base.html                # Sidebar template framework & navbar toggle
    ├── login.html               # Dual sign-in and registration forms
    ├── dashboard.html           # Score gauges, daily checklist, & "What Should I Do Now?" modal
    ├── profile.html             # Profile editor and target package selectors
    ├── academics.html           # Subject logs, course credits, & priority agenda lists
    ├── skills.html              # Roadmap grid tabs & interactive status selectors
    ├── planner.html             # Daily schedule time block builder
    ├── projects.html            # Portfolio project tracker, milestone checklists & AI blueprints
    ├── resume.html              # CV checklists and writing tips
    └── analytics.html           # Interactive charts & study logger
```

---

## 🛠️ Manual CLI Installation & Setup

1. **Install Dependencies**:
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   py database_init.py
   ```

3. **Run Application Server**:
   ```bash
   py app.py 8080
   ```
