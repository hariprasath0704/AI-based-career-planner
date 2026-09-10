# PathPilot – AI Academic & Career Planner: Full Project Report

---

## 📌 Executive Summary
**PathPilot** is an AI-powered, full-stack college companion web application built to guide engineering and technology students through academic course management, skill development, portfolio project tracking, and placement preparation. 

It solves the common student dilemma of not knowing **what to study next**, **how to balance academics and coding projects**, and **whether they are on track to achieve their placement goals**.

---

## 💡 What Makes PathPilot Useful? (Key Student Benefits)

1. **Eliminates Decision Fatigue ("What Should I Do Now?")**:
   - Instead of guessing what to study, students click **"What Should I Do Now?"** to receive an instant AI recommendation computed using mathematical urgency, difficulty, importance, and job track relevance.

2. **Automated Syllabus & Deadline Tracking**:
   - Tracks subjects with course credits and target grades while dynamically calculating overall syllabus coverage from completed tasks.
   - Highlights tasks with color-coded deadline badges (`Overdue`, `Due Today`, `Remaining Days`).

3. **Placement Career Alignment Matrix**:
   - Uses **Cosine Similarity ML algorithms** to calculate how closely a student's current skill profile matches real-world target job profiles (e.g., Software Development Engineer, ML Engineer, Web Developer).

4. **Portfolio-Grade Project Planner with Milestones**:
   - Projects feature sub-task milestone checklists. Checking off sub-tasks automatically updates project completion percentages in real-time.
   - Provides **1-Click AI Project Blueprints** so students can adopt resume-worthy projects with pre-populated tasks.

5. **Integrated 1-Click Study Logger**:
   - Students can log 30-minute or 60-minute study blocks directly on tasks, updating subject progress and populating historic analytics graphs automatically.

6. **Resume Readiness & Scoring**:
   - Computes a 100-point placement readiness score evaluating academics (CGPA/arrears), core roadmap skills, portfolio projects, and resume completeness.

---

## 🛠️ Complete List of Options Available in PathPilot

### 1. Account & Security Options
* **Login & Registration:** User authentication with encrypted password hashing (`Werkzeug`).
* **Session Management:** Profile isolation per logged-in user.

### 2. Student Profile Options
* **Academic Details:** Department, Year, Semester, CGPA, and Arrear count.
* **Placement Goals:** Target Role (SDE, Web Dev, ML Engineer), Target Company (Google, Amazon, etc.), and Target Salary.
* **Daily Preferences:** Daily Available Study Hours slider and learning streak counter.

### 3. Academic Planner Options
* **Subject Registration:** Name, Course Credits (1-10), and Target Grade (`S/O`, `A+`, `A`, `B+`, `B`).
* **Syllabus Progress Tracker:** Visual progress bars with edit and delete capabilities.
* **Task Registration:** Topic/Unit name, Linked Subject, Task Type (`Assignment`, `Exam/Test`, `Revision`, `Study Chapter`, `Lab Practical`), Deadline date, Difficulty (1-5), and Importance (1-5).
* **Priority Queue Sorting:** Tasks are automatically categorized into **High**, **Medium**, and **Low Priority** buckets.
* **⚡ +30m Study Logger:** Instant button to log study time and elevate task completion %.

### 4. Project Tracker & Portfolio Options
* **Register Portfolio Project:** Title, Tech Stack, Description, GitHub Repository URL, Live Demo URL, Status (`Idea Phase`, `In Progress`, `Testing`, `Completed`), and Completion %.
* **Milestone Checklist System:** Add custom sub-tasks, toggle completion checkboxes (auto-calculates overall progress %), and delete steps.
* **⚡ Adopt AI Blueprint:** 1-click import of recommended career projects with pre-configured milestone steps.
* **Portfolio Readiness Summary:** Header banner displaying project health against target job tracks.

### 5. Placement Skill Roadmap Options
* **Skill Category Tabs:** 5 categorized grids (`Programming`, `Core CS`, `Development`, `AIML`, `Placement & Interviews`).
* **Status Controls:** AJAX status dropdowns (`Not Started`, `Learning`, `Practicing`, `Completed`).

### 6. AI Recommendation System Options
* **Cosine Similarity Career Alignment Match %**
* **Career Skill Gap Analyzer** (identifies uncompleted core skills for target companies)
* **Weak Domain Index**
* **Daily Priority Action Cards** with time estimates and benefit notes
* **Day-by-Day Weekly Strategy Schedule**

### 7. Daily Planner Options
* **Dynamic Schedule Generator:** Divides available daily hours into 45-minute focus blocks and 15-minute breaks.
* **Interactive Time Slot Checkboxes:** Check off study slots as you complete them throughout the day.

### 8. Resume Tracker Options
* **100-Point Resume Strength Gauge**
* **5-Section Completeness Checklist:** Summary, Education, Work/Experience, Projects, Technical Skills.
* **Google XYZ Formula Guide & Role Keyword Advice**

### 9. Progress Analytics Options
* **Weekly Study Hours Chart** (Line graph)
* **Skill Category Coverage Chart** (Bar graph)
* **Subject Syllabus Progress Chart** (Horizontal Bar graph)
* **Historic Placement Readiness Trend Line**

### 10. User Interface Options
* **Light / Dark Mode Toggle Switch:** Persistent theme switching across all pages.

---

## 🏷️ HTML, Bootstrap, Jinja2 & CSS Tags/Components Used

### 1. Semantic HTML5 Tags
* `<header>`, `<main>`, `<aside>`, `<nav>`, `<section>`, `<article>`, `<footer>` – Structured layout architecture.
* `<form>`, `<input>`, `<select>`, `<option>`, `<textarea>`, `<button>`, `<label>` – Interactive data inputs.
* `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` – Structured priority agendas, weekly schedules, and skill gap tables.
* `<div>`, `<span>`, `<small>`, `<strong>`, `<h6>`, `<h5>`, `<h4>`, `<h2>`, `<h1>` – Content hierarchy and text formatting.
* `<canvas>` – Dynamic rendering element for Chart.js analytics graphs.

### 2. Jinja2 Templating Syntax & Tags
* `{% extends 'base.html' %}` – Inherits the main sidebar and master page template.
* `{% block content %}` ... `{% endblock %}` – Page-specific content insertion.
* `{% macro render_task_row(...) %}` ... `{% endmacro %}` – Reusable component rendering macros.
* `{% if ... %}` ... `{% elif ... %}` ... `{% else %}` ... `{% endif %}` – Conditional rendering for priority queues, badges, and empty state fallbacks.
* `{% for item in collection %}` ... `{% endfor %}` – Iterative looping over subjects, tasks, projects, milestones, and skills.
* `{{ variable | filter }}` – Variable interpolation with Jinja filters (`|length`, `|round(1)`, `|int`, `|abs`, `|selectattr`).

### 3. Bootstrap 5 Framework Components & Utility Classes
* **Grid Layout System:** `.row`, `.col-12`, `.col-lg-8`, `.col-md-6`, `.col-lg-4`, `.g-3`, `.g-4`
* **Card & Panel Styling:** `.path-card`, `.bg-light-subtle`, `.bg-primary-subtle`, `.shadow-sm`, `.border`, `.rounded-4`
* **Badges & Pills:** `.badge`, `.text-bg-danger`, `.text-bg-warning`, `.text-bg-success`, `.text-bg-light`, `.rounded-pill`
* **Buttons & Controls:** `.btn`, `.btn-primary`, `.btn-outline-primary`, `.btn-success`, `.btn-danger`, `.btn-sm`, `.rounded-3`
* **Forms & Switches:** `.form-control`, `.form-select`, `.form-check`, `.form-switch`, `.input-group`
* **Modal Dialogs:** `.modal`, `.modal-dialog-centered`, `.modal-content`, `.modal-header`, `.modal-body`, `.modal-footer`
* **Accordion:** `.accordion`, `.accordion-item`, `.accordion-button`, `.accordion-collapse`
* **Progress Bars:** `.progress-container`, `.progress-bar-fill`

### 4. FontAwesome 6 Icon Tags (`<i class="...">`)
* `<i class="fa-solid fa-graduation-cap">` – Academic Planner
* `<i class="fa-solid fa-code">` – Project Tracker
* `<i class="fa-solid fa-brain">` – AI Recommendations
* `<i class="fa-solid fa-chart-line">` – Dashboard
* `<i class="fa-solid fa-fire">` – Learning Streak
* `<i class="fa-solid fa-bolt">` – Fast Study Session Logger
* `<i class="fa-solid fa-rocket">` – Career Goals
* `<i class="fa-brands fa-github">` – GitHub Codebase links
* `<i class="fa-solid fa-globe">` – Live Demo links

---

## 🧮 AI / Machine Learning & Mathematical Models

### 1. Cosine Similarity Alignment Formula
$$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$
* **Vector $A$**: Student's skill vector weighted by completion state (`Completed=1.0`, `Practicing=0.7`, `Learning=0.4`, `Not Started=0.0`).
* **Vector $B$**: Blueprint vector required for the target career role.

### 2. Task Priority Score Heuristic Formula
$$\text{Priority Score} = \text{Urgency} + (\text{Difficulty} \times 1.5) + (\text{Importance} \times 1.5) + \text{Remaining Work Weight}$$
* **Urgency**: $\max(0, 10 - \text{Days Until Deadline})$ (Overdue tasks receive score 12).
* **Remaining Work**: $\left(\frac{100 - \text{Completion \%}}{100}\right) \times 8$.

### 3. Placement Readiness Index Formula (0 - 100 Points)
$$\text{Readiness Score} = \text{Academic Score (20)} + \text{Core Skills (30)} + \text{Applied Skills (20)} + \text{Placement Prep (15)} + \text{Portfolio \& Resume (15)}$$

---

## 🗄️ Database Architecture (`models.py`)

* **`User`**: User accounts (username, email, password hash).
* **`StudentProfile`**: Profile info (name, department, year, semester, CGPA, arrears, daily available hours, streak).
* **`PlacementGoal`**: Career goals (target role, target company, target salary, resume score, resume JSON checklist).
* **`Subject`**: Course subjects (name, progress %, credits, target grade).
* **`AcademicTask`**: Assignment/Exam tasks (topic, task type, deadline, difficulty, importance, completion %, priority score).
* **`Skill` & `StudentSkill`**: Placement roadmap skills categorized by domain.
* **`Project`**: Portfolio projects (name, technology, description, github_link, live_demo_link, status, completion %, milestones_json).
* **`DailyPlan`**: Dynamic study time slots.
* **`StudySession`**: Logged study sessions for analytics graphs.
* **`Recommendation`**: Generated AI recommendation notes.

---

## 🚀 How to Run in Visual Studio Code (Quick Reference)

1. **Open Project Folder in VS Code:** `c:\Users\harip_dg7cw87\Downloads\DNN  project\new my project path pilot`
2. **Press `F5`** (or open terminal with `Ctrl + ~` and run `py app.py 8080`).
3. **Open Browser:** **[http://127.0.0.1:8080](http://127.0.0.1:8080)**
4. **Login:** Username `student` | Password `student123`
